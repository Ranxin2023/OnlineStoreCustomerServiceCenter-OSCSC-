@echo off
set DEFAULT_CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe
set DEFAULT_USER_DATA=C:\Users\%USERNAME%\chrome-selenium

set /p CHROME_PATH="Chrome path [%DEFAULT_CHROME%]: "
if "%CHROME_PATH%"=="" set CHROME_PATH=%DEFAULT_CHROME%

set /p CHROME_USER_DATA="User data dir [%DEFAULT_USER_DATA%]: "
if "%CHROME_USER_DATA%"=="" set CHROME_USER_DATA=%DEFAULT_USER_DATA%

echo CHROME_PATH=%CHROME_PATH%> .env
echo CHROME_USER_DATA=%CHROME_USER_DATA%>> .env

echo.
echo .env file created!
echo CHROME_PATH=%CHROME_PATH%
echo CHROME_USER_DATA=%CHROME_USER_DATA%
pause