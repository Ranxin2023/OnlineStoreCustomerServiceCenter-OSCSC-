@echo off
echo CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe> ./backend/.env
echo CHROME_USER_DATA=C:\Users\%USERNAME%\chrome-selenium>> ./backend/.env
echo .env file created!
echo "点任意键继续"
pause > nul