@REM 参考@Mark4551124015的pr https://github.com/JustMachiavelli/javsdt/pull/119
@echo off
chcp 65001
mode con cols=81 lines=20
TITLE Javsdt打包工具

:MENU
CLS
echo.
echo.                                      打包工具
ECHO. ===============================================================================
echo. =                                                                             =
echo. =         [1]打包 素人Jav321  [2]打包 创建ini    [3] 打包 javdbFc2            =
echo. =                                                                             =
echo. =         [4]打包 Javbus无码  [5]打包 Javbus有码 [6] 打包 Javlib有码          =
echo. =                                                                             =
ECHO. ===============================================================================
echo.
echo.
:choice
set choice=
set /p choice= 请输入选项:
if /i "%choice%"=="1" goto Createini
if /i "%choice%"=="2" goto Youma
if /i "%choice%"=="3" goto BusW
if /i "%choice%"=="4" goto Suren
if /i "%choice%"=="5" goto Fc2
echo. 输入无效
echo.
goto choice


:Createini
echo. 开始打包CreateIni
pyinstaller -F CreateIni.py
cd dist
move /y CreateIni.exe 重新创建ini.exe
goto end

:Youma
echo. 开始打包Youma.py
pyinstaller -F Youma.py -i
cd dist
@REM move /y javlibrary.exe 【有码】javlibrary.exe
goto end

:BusW
echo. 开始打包
pyinstaller -F -i favicon.ico JavBusWuma.py
cd dist
move /y JavBusWuma.exe 【无码】Javbus.exe
goto end

:jav321
echo. 开始打包Jav321
pyinstaller -F Jav321.py
cd %~dp0\dist
move /y "Jav321.exe" "【素人】jav321 须翻墙.exe"
goto end

:Fc2
echo. 开始打包
pyinstaller -F JavdbFc2.py
cd dist
move /y "JavdbFc2.exe" 【FC2】javdb.exe
goto end

:end
echo. 回车继续打包
pause 1>nul 2>nul
cd ..
goto MENU