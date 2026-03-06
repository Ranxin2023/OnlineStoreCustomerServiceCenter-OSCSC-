@echo off

echo Creating .env file...

(
echo VITE_LOCALHOST_API_URL=http://localhost:5001
echo CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
echo CHROME_USER_DATA=C:\Users\%USERNAME%\chrome-selenium
echo BASE_URL=https://csp.aliexpress.com
echo DEBUG_PORT=9222
) > OnlineStoreCustomerServiceCenter-OSCSC--main/.env

echo Finish setting up
pause