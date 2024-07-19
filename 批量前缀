@echo off
setlocal enabledelayedexpansion

rem 设置文件路径
set "path=*************"
rem 设置前缀
set "prefix=***********"

rem 切换到指定目录
cd /d "%path%"

rem 遍历目录下的所有文件
for %%f in (*.*) do (
    ren "%%f" "%prefix%%%f"
)

endlocal
pause
