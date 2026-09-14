@echo off
setlocal
echo ===================================================
echo   IT'S MY AI -- PUSH TO GITHUB CLOUD BUILDER
echo ===================================================
echo.
echo Please create a new empty repository at:
echo   https://github.com/new
echo (Name it: its-my-ai, make it Private or Public, do NOT check README or .gitignore)
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/its-my-ai.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered. Aborting.
    pause
    exit /b 1
)

echo.
echo [1/3] Setting remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] Renaming branch to main...
git branch -M main

echo [3/3] Pushing to GitHub...
git push -u origin main

echo.
echo ===================================================
echo   DONE! Go to the 'Actions' tab on your GitHub repo.
echo   GitHub is now automatically building your APK!
echo ===================================================
pause
