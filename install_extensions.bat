@echo off
title IT'S MY AI - Universal Extensions Installer
echo ========================================================
echo         INSTALLING RECOMMENDED EXTENSIONS
echo ========================================================
echo.
echo [1/2] Installing Python packages from requirements.txt...
python -m pip install -r requirements.txt
echo.
echo [2/2] Checking for editor extension CLI installer...
where code >nul 2>nul
if %errorlevel% equ 0 (
    echo Installing extensions in editor...
    code --install-extension ms-python.python
    code --install-extension ms-python.vscode-pylance
    code --install-extension charliermarsh.ruff
    code --install-extension usernamehw.errorlens
    code --install-extension aaron-bond.better-comments
    code --install-extension ritwickdey.liveserver
    code --install-extension esbenp.prettier-vscode
    code --install-extension ecmel.vscode-html-css
    code --install-extension formulahendry.auto-close-tag
    code --install-extension formulahendry.auto-rename-tag
    code --install-extension humao.rest-client
    code --install-extension mikestead.dotenv
    code --install-extension mechatroner.rainbow-csv
    echo.
    echo All extensions installed successfully!
) else (
    echo 'code' CLI not found in system PATH.
    echo.
    echo Direct 1-Click GUI Method:
    echo 1. Press Ctrl+Shift+X in your editor
    echo 2. Type: @recommended
    echo 3. Click "Install" on each extension
)
echo.
pause
