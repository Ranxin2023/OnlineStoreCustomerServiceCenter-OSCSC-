@echo off
set DEFAULT_API_URL=http://localhost:5000

set /p VITE_API_URL="API URL [%DEFAULT_API_URL%]: "
if "%VITE_API_URL%"=="" set VITE_API_URL=%DEFAULT_API_URL%

echo VITE_API_URL=%VITE_API_URL%> .env

echo.
echo .env file created!
echo VITE_API_URL=%VITE_API_URL%
pause