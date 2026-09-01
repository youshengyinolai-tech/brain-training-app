# Windows用 exe の作り方(開発者向け)

施設のパソコンはオフライン運用なので、**インターネットに繋がる別のWindowsパソコン**で
一度だけ `脳トレメーカー.exe` をビルドし、それを施設のパソコンにコピーします。
ビルドしたパソコン側はネットが必要ですが、出来上がった exe は施設のパソコン側で
ネット無しで動作します。

## 必要なもの

- Windows PC(インターネット接続あり)
- Python 3.10以降(インストール時に「Add python.exe to PATH」に必ずチェック)
  https://www.python.org/downloads/windows/

## 手順

1. このフォルダ一式(`brain-training-app`)を、ビルド用のWindows PCにコピーします。
2. `build_windows_exe.bat` をダブルクリックします。
   - 初回はPythonパッケージのダウンロードで数分かかります。
   - 完了すると `dist\脳トレメーカー.exe` が出来上がります。
3. `dist\脳トレメーカー.exe` を USBメモリ等で施設のパソコンにコピーします。
   - exeファイル1つだけで動作します(フォントも中に同梱済みです)。
   - 施設のパソコン側でPythonをインストールする必要はありません。

## 動作確認したいとき(このビルドPC上で)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 内容を変更したいとき

`braintrain/` フォルダの中の Python ファイルを編集後、
もう一度 `build_windows_exe.bat` を実行すれば新しい exe が作られます。

- `braintrain/maze.py` … めいろの生成
- `braintrain/odd_one_out.py` … なかまはずれさがしの生成
- `braintrain/spot_diff.py` … まちがいさがしの生成
- `braintrain/shapes.py` … 図形の描画(色・形の定義もここ)
- `braintrain/gui.py` … 画面(ボタンなど)
- `braintrain/pdf_common.py` … PDFの共通レイアウト・フォント読み込み

## 注意

- `assets/fonts/` の日本語フォント(Noto Sans JP)は Google の SIL Open Font License 1.1 で
  自由に再配布可能なフォントです。`assets/fonts/OFL.txt` にライセンス全文があります。
- macOS版のexeを作りたい場合は、Macで同じ手順(`pyinstaller --onefile --windowed
  --add-data "assets:assets" main.py`、区切り文字が `:` になる点に注意)を実行してください。
