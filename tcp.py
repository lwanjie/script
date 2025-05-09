import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkFont
from queue import Queue
from PIL import Image, ImageTk # <--- 导入Pillow库

# --- 配置 ---
HOST = '0.0.0.0'
PORT = 8269
BUFFER_SIZE = 1024
data_queue = Queue()

# --- 数据解析函数 (已更新以处理7个数据点) ---
def parse_sensor_data(data_str):
    # 数据格式: "#temp,humidity,pm2.5,co2,voc,pm1,pm10#"
    if not data_str.startswith("#") or not data_str.endswith("#"):
        return None
    try:
        stripped_data = data_str[1:-1]
        parts = stripped_data.split(',')
        if len(parts) != 7: # <--- 检查7个数据部分
            # log_to_gui(f"数据段数量错误: 期望7个，实际{len(parts)} - {data_str}\n") # 避免在非GUI线程直接调用GUI相关
            print(f"数据段数量错误: 期望7个，实际{len(parts)} - {data_str}") # 打印到控制台
            return None

        temperature = float(parts[0])
        humidity = float(parts[1])
        pm25 = int(parts[2])
        co2 = int(parts[3])
        voc_raw = int(parts[4])
        pm1 = int(parts[5])   # <--- 新增PM1
        pm10 = int(parts[6])  # <--- 新增PM10

        voc_quality_map = {1: "优", 2: "良", 3: "中", 4: "差"}
        voc_quality = voc_quality_map.get(voc_raw, f"未知 ({voc_raw})")
        return {
            "temperature": temperature, "humidity": humidity, "pm25": pm25,
            "co2": co2, "voc_raw": voc_raw, "voc_quality": voc_quality,
            "pm1": pm1, "pm10": pm10, # <--- 添加到返回字典
            "raw_string": data_str
        }
    except ValueError as e:
        print(f"数据值转换错误: {e} - {data_str}")
        return None
    except Exception as e:
        print(f"解析数据时发生未知错误: {e} - {data_str}")
        return None

# --- 日志记录到GUI ---
def log_to_gui(message):
    data_queue.put(f"LOG:{message}")

# --- 处理客户端连接的函数 ---
def handle_client_connection(client_socket, client_address):
    log_to_gui(f"[新连接] {client_address} 已连接。\n")
    data_buffer = ""
    try:
        while True:
            request_bytes = client_socket.recv(BUFFER_SIZE)
            if not request_bytes:
                log_to_gui(f"[断开连接] {client_address} 已断开。\n")
                break
            data_buffer += request_bytes.decode('utf-8', errors='ignore')
            while True:
                start_index = data_buffer.find('#')
                if start_index == -1: break
                end_index = data_buffer.find('#', start_index + 1)
                if end_index == -1:
                    if len(data_buffer) > BUFFER_SIZE * 2:
                        log_to_gui(f"[警告] 来自 {client_address} 的数据缓冲区过长且消息不完整。尝试保留起始部分。\n")
                        data_buffer = data_buffer[start_index:]
                    break
                complete_message = data_buffer[start_index : end_index + 1]
                data_buffer = data_buffer[end_index + 1 :]
                parsed_data = parse_sensor_data(complete_message)
                if parsed_data:
                    parsed_data['client_address'] = client_address
                    data_queue.put(parsed_data)
                else:
                    log_to_gui(f"[{client_address}] 数据解析失败: {complete_message}\n")
    except ConnectionResetError:
        log_to_gui(f"[连接重置] {client_address} 连接被重置。\n")
    except socket.timeout:
        log_to_gui(f"[超时] {client_address} 连接超时。\n")
    except Exception as e:
        log_to_gui(f"[错误] 处理 {client_address} 时发生错误: {e}\n")
    finally:
        log_to_gui(f"[关闭连接] 关闭与 {client_address} 的连接。\n")
        client_socket.close()

# --- 启动TCP服务器的函数 ---
def start_tcp_server(gui_app_instance):
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        log_to_gui(f"[状态] 服务器正在监听 {HOST}:{PORT}\n")

        while gui_app_instance.server_running:
            try:
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(60)
                client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address), daemon=True)
                client_thread.start()
            except socket.error as e:
                if gui_app_instance.server_running:
                    log_to_gui(f"[服务器错误] accept失败: {e}\n")
                break
            except Exception as e:
                if gui_app_instance.server_running:
                     log_to_gui(f"[服务器意外错误]: {e}\n")
                break
    except OSError as e:
        log_to_gui(f"[服务器错误] 无法启动服务器于 {HOST}:{PORT} - {e}\n")
        messagebox.showerror("服务器错误", f"无法启动服务器于 {HOST}:{PORT}。\n端口可能已被占用或无权限。\n错误: {e}")
    except Exception as e:
        log_to_gui(f"[服务器致命错误] {e}\n")
        messagebox.showerror("服务器致命错误", f"发生意外错误: {e}")
    finally:
        log_to_gui("[状态] 服务器已停止。\n")
        if server_socket:
            server_socket.close()
        if gui_app_instance.server_running:
            gui_app_instance.server_running = False
            gui_app_instance.update_status_indicator(False)


class SensorDisplayApp:
    def __init__(self, master):
        self.master = master
        master.title(f"空气质量监测上位机 (监听 {HOST}:{PORT})")
        master.geometry("800x600") # 调整窗口大小以适应新布局和图片

        self.server_thread = None
        self.server_running = False

        # --- 字体定义 ---
        self.font_ui_chinese_s10 = tkFont.Font(family="SimSun", size=10)
        self.font_ui_chinese_s11 = tkFont.Font(family="SimSun", size=11)
        self.font_ui_chinese_s12_bold = tkFont.Font(family="SimSun", size=12, weight="bold")
        self.font_data_western_s12 = tkFont.Font(family="Times New Roman", size=12)
        self.font_log_western_s9 = tkFont.Font(family="Times New Roman", size=9)

        # --- 加载图片资源 ---
        self.bg_image_tk = None
        self.start_icon_tk = None
        self.stop_icon_tk = None

        try:
            # **用户需要提供 background.png, start_icon.png, stop_icon.png 文件**
            # 或修改为实际的图片路径和文件名
            img_path = "" # 如果图片在脚本同目录，此路径为空即可
            
            # 背景图片
            bg_pil_image = Image.open(img_path + "background.png")
            # bg_pil_image = bg_pil_image.resize((800, 600), Image.Resampling.LANCZOS) # 可选：调整背景图大小
            self.bg_image_tk = ImageTk.PhotoImage(bg_pil_image)

            # 按钮图标 (调整大小以适应按钮)
            start_pil_image = Image.open(img_path + "start_icon.png").resize((20, 20), Image.Resampling.LANCZOS)
            self.start_icon_tk = ImageTk.PhotoImage(start_pil_image)
            
            stop_pil_image = Image.open(img_path + "stop_icon.png").resize((20, 20), Image.Resampling.LANCZOS)
            self.stop_icon_tk = ImageTk.PhotoImage(stop_pil_image)

        except FileNotFoundError as e:
            log_to_gui(f"LOG:警告: 图片文件未找到 ({e.filename})。\n")
        except Exception as e:
            log_to_gui(f"LOG:错误: 加载图片时出错 - {e}\n")


        # --- 主布局框架 ---
        main_frame = tk.Frame(master) # padx, pady 可以移到这里，或保持在master上
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 设置背景图片 ---
        if self.bg_image_tk:
            bg_label = tk.Label(main_frame, image=self.bg_image_tk)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1, anchor="nw")
            # 注意：其他控件需要放置在main_frame之上，并且如果它们有自己的背景色，会覆盖背景图。
            # 如果希望LabelFrame等透明，需要更复杂的技巧或使其背景与图片协调。

        # --- 状态标签 ---
        self.status_label = tk.Label(main_frame, text="服务器状态: 未运行", fg="red", font=self.font_ui_chinese_s11)
        # 如果背景图颜色较深，可能需要设置status_label的背景色以保证可读性，例如: self.status_label.config(bg="white")
        self.status_label.pack(pady=(0, 10))

        # --- 控制按钮 ---
        control_frame = tk.Frame(main_frame) # , bg="red") # test
        if self.bg_image_tk: # 如果有背景图，让此frame背景“透明”（实际是继承父容器特性）
             control_frame.config(bg=main_frame.cget('bg')) # 尝试获取父背景，可能不完美
        control_frame.pack(pady=(0, 10))
        
        self.start_button = tk.Button(control_frame, text="启动", command=self.start_server,
                                       image=self.start_icon_tk, compound=tk.LEFT,  # 图片在文字左侧
                                       font=self.font_ui_chinese_s10, padx=5) # padx给文字和图标间留空
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="停止", command=self.stop_server, state=tk.DISABLED,
                                      image=self.stop_icon_tk, compound=tk.LEFT,
                                      font=self.font_ui_chinese_s10, padx=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)


        # --- 数据展示区 (使用 grid 布局) ---
        data_frame = tk.LabelFrame(main_frame, text="实时数据", padx=15, pady=10, font=self.font_ui_chinese_s12_bold)
        # data_frame.config(bg="lightyellow") # 可以给LabelFrame设置背景色，使其在背景图上突出
        data_frame.pack(fill="x", pady=(0, 10))

        # StringVars for data display
        self.temp_var = tk.StringVar(value="温度: -- °C")
        self.hum_var = tk.StringVar(value="湿度: -- %")
        self.pm25_var = tk.StringVar(value="PM2.5: -- µg/m³")
        self.co2_var = tk.StringVar(value="CO2: -- ppm")
        self.voc_var = tk.StringVar(value="空气质量: --")
        self.pm1_var = tk.StringVar(value="PM1: -- µg/m³")   # <--- 新增PM1 StringVar
        self.pm10_var = tk.StringVar(value="PM10: -- µg/m³") # <--- 新增PM10 StringVar

        # Create Labels for data
        temp_label = tk.Label(data_frame, textvariable=self.temp_var, font=self.font_data_western_s12)
        hum_label = tk.Label(data_frame, textvariable=self.hum_var, font=self.font_data_western_s12)
        pm25_label = tk.Label(data_frame, textvariable=self.pm25_var, font=self.font_data_western_s12)
        pm1_label = tk.Label(data_frame, textvariable=self.pm1_var, font=self.font_data_western_s12) # <--- 新增PM1 Label
        pm10_label = tk.Label(data_frame, textvariable=self.pm10_var, font=self.font_data_western_s12) # <--- 新增PM10 Label
        co2_label = tk.Label(data_frame, textvariable=self.co2_var, font=self.font_data_western_s12)
        voc_label = tk.Label(data_frame, textvariable=self.voc_var, font=self.font_ui_chinese_s11) # VOC用中文优先字体

        # Grid layout for data labels (4 items in row 0, 3 items in row 1)
        # Row 0
        temp_label.grid(row=0, column=0, sticky="w", padx=10, pady=3)
        hum_label.grid(row=0, column=1, sticky="w", padx=10, pady=3)
        pm25_label.grid(row=0, column=2, sticky="w", padx=10, pady=3)
        pm1_label.grid(row=0, column=3, sticky="w", padx=10, pady=3)
        # Row 1
        pm10_label.grid(row=1, column=0, sticky="w", padx=10, pady=3)
        co2_label.grid(row=1, column=1, sticky="w", padx=10, pady=3)
        voc_label.grid(row=1, column=2, sticky="w", padx=10, pady=3)
        
        # 让列平均分配空间 (可选, 如果希望它们对齐或居中)
        for i in range(4): # 假设最多4列
            data_frame.grid_columnconfigure(i, weight=1)


        # --- 日志区域 ---
        log_frame = tk.LabelFrame(main_frame, text="运行日志", padx=10, pady=5, font=self.font_ui_chinese_s12_bold)
        # log_frame.config(bg="lightblue") # 可以给LabelFrame设置背景色
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8, state=tk.DISABLED, font=self.font_log_western_s9)
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)

        self.master.after(100, self.process_queue)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.status_label.config(text="服务器状态: 启动中...", fg="orange")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.server_thread = threading.Thread(target=start_tcp_server, args=(self,), daemon=True)
            self.server_thread.start()
        else:
            log_to_gui("[GUI] 服务器已经在运行中。\n")

    def stop_server(self):
        if self.server_running:
            log_to_gui("[GUI] 请求停止服务器...\n")
            self.server_running = False
            connect_host = '127.0.0.1' if HOST == '0.0.0.0' else HOST
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    s.connect((connect_host, PORT))
            except Exception: pass
            if self.server_thread and self.server_thread.is_alive():
                 self.server_thread.join(timeout=1.5)
            self.update_status_indicator(False)
        else:
            log_to_gui("[GUI] 服务器尚未运行。\n")

    def update_status_indicator(self, running):
        if running:
            self.status_label.config(text="服务器状态: 运行中", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="服务器状态: 已停止", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def update_log_display(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def process_queue(self):
        try:
            while True:
                item = data_queue.get_nowait()
                if isinstance(item, dict):
                    self.temp_var.set(f"温度: {item['temperature']:.1f} °C")
                    self.hum_var.set(f"湿度: {item['humidity']:.1f} %")
                    self.pm25_var.set(f"PM2.5: {item['pm25']} µg/m³")
                    self.co2_var.set(f"CO2: {item['co2']} ppm")
                    self.voc_var.set(f"空气质量: {item['voc_quality']} (原始值: {item['voc_raw']})")
                    self.pm1_var.set(f"PM1: {item['pm1']} µg/m³")     # <--- 更新PM1显示
                    self.pm10_var.set(f"PM10: {item['pm10']} µg/m³")   # <--- 更新PM10显示

                    client_addr_str = "未知客户端"
                    if 'client_address' in item and isinstance(item['client_address'], tuple) and len(item['client_address']) == 2:
                         client_addr_str = f"来自 {item['client_address'][0]}:{item['client_address'][1]}"
                    self.update_log_display(f"数据: {item['raw_string']} ({client_addr_str})\n")

                elif isinstance(item, str) and item.startswith("LOG:"):
                    log_msg = item[4:]
                    self.update_log_display(log_msg)
                    if "[状态] 服务器正在监听" in log_msg:
                        self.update_status_indicator(True)
                    elif "[状态] 服务器已停止" in log_msg or \
                         "无法启动服务器" in log_msg or \
                         "服务器致命错误" in log_msg:
                        self.update_status_indicator(False)
        except Exception: pass
        finally:
            self.master.after(100, self.process_queue)

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出应用程序吗？这将停止服务器。"):
            self.stop_server()
            if self.server_thread is not None and self.server_thread.is_alive():
                self.server_thread.join(timeout=1)
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDisplayApp(root)
    root.mainloop()
