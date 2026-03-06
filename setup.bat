@echo off
echo LOCALHOST_URL=http://localhost:5000 >> .env
echo CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe>> .env
echo CHROME_USER_DATA=C:\Users\%USERNAME%\chrome-selenium >> .env
echo BASE_URL= "https://csp.aliexpress.com" >> .env
echo DEBUG_PORT=9222 >> .env
echo "Finish setting up"