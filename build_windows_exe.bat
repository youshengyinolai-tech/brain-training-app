@echo off
setlocal

echo ============================================
echo   脳トレメーカー - Windows用 exe 作成スクリプト
echo   (このパソコンにネット接続が必要です。1回だけ実行すればOK)
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    echo   https://www.python.org/downloads/windows/ から Python をインストールしてから
    echo   もう一度このファイルをダブルクリックしてください。
    echo   （インストール時に「Add python.exe to PATH」に必ずチェックを入れてください）
    pause
    exit /b 1
)

if not exist venv (
    echo [1/4] 作業用のPython環境を作成しています...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [2/4] 必要な部品をインストールしています...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo [3/4] exe ファイルを作成しています（数分かかることがあります）...
pyinstaller --noconfirm --onefile --windowed ^
    --name "脳トレメーカー" ^
    --add-data "assets;assets" ^
    main.py

echo [4/4] 完了しました。
echo.
echo dist フォルダの中の「脳トレメーカー.exe」を
echo 施設のパソコンにコピーしてお使いください。
echo （このexeファイル1つだけで動きます。ネット接続は不要です）
echo.
pause
