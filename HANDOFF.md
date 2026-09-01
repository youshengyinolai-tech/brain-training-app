# 引き継ぎ書 — 脳トレメーカー

作成: Claude (Claude Code) / 2026-09-01
引き継ぎ先: ChatGPT（以降の作業を継続）

## 1. プロジェクトの目的

介護施設に「お世話になったお礼」として、脳トレ教材を自動生成するツールを置き土産として渡す。

要件（ユーザーからのヒアリング内容）:
- 施設のPCはネット接続なし・ソフトのインストールができない可能性がある
- 職員がボタンを押すたびに新しい問題が自動生成される（作り置きではない）
- 内容は「間違い探し・図形・迷路」中心

この制約から、**Pythonデスクトップアプリ（PyInstaller製exe）ではなく、
ブラウザで完結する単一HTMLファイル**を正式な配布形態として採用した。

## 2. 現在の状態（完了済み）

### リポジトリ・公開URL
- GitHubリポジトリ（公開）: https://github.com/youshengyinolai-tech/brain-training-app
- GitHub Pages: https://youshengyinolai-tech.github.io/brain-training-app/
  （ルートの `index.html` が `web/脳トレメーカー.html` へ自動リダイレクト）
- GitHubアカウント: `youshengyinolai-tech`（このマシンで `gh` CLI 認証済み。
  `~/.config/gh` が root所有で書き込めない環境だったため、
  `GH_CONFIG_DIR=~/.gh-config` を都度指定して認証・push している）

### 本体ファイル: `web/脳トレメーカー.html`
- 完全に単一ファイル（CSS/JSともにインライン、外部リソース依存ゼロ）
- ネット接続不要（一度ローカルにコピーすれば完全オフラインで動作）
- インストール不要（ダブルクリックしてブラウザで開くだけ）
- 実装済み機能:
  - **めいろ**: 再帰的バックトラッキング法でグリッド迷路を生成。解答ページ（赤線でルート表示）付き
  - **なかまはずれさがし**: 丸・四角・三角・星・ひし形の図形グリッドから1つだけ違うもの
    （色/形が違う）を探す。1ページに4問配置
  - **まちがいさがし**: 上下2つの図形シーンを見比べる。差分は「色変更」「サイズ変更」
    「消失」の3種、5〜7箇所（難易度による）。現在は幾何学図形のみ（下記「未完了」参照）
  - 難易度3段階（やさしい/ふつう/むずかしい）、こたえページ表示のON/OFF切替
  - 印刷は `window.print()` を発火。CSSの `@media print` でA4サイズ（`.sheet` divを
    210mm×297mm固定、`@page{size:A4;margin:0}`）に整形、複数ページは`page-break-after`

### Python版（初期プロトタイプ、現在は「参考・予備」扱い）
- `main.py` / `braintrain/*.py` / `build_windows_exe.bat` / `BUILD.md`
- fpdf2でPDF生成 → PyInstallerでWindows exe化する方式で最初に作ったもの
- Web版を作った後は使っていない。README.mdにも「参考・予備」と明記済み
- 削除してよいかはユーザー未確認（残しておいても実害はない）

### テスト方法（このセッションで実施した手順、再現用）
このマシンには Node.js と Google Chrome.app があり、`puppeteer-core` で
既存のChromeを headless 起動してテストした（Playwrightや独自Chromiumのダウンロードは不要）。
```
npm install puppeteer-core
```
→ `page.goto("file://.../脳トレメーカー.html")` → 各ボタンをクリック
→ `page.pdf({printBackground:true, preferCSSPageSize:true})` で印刷結果をPDF化
→ `pymupdf`（`python3 -c "import fitz"`）でPDFをPNGにラスタライズして目視確認、
というループでバグを2つ発見・修正済み（日本語ラベルのfont-family抜け／
まちがいさがしページ下段パネルとフッターの重なり）。同じ手順で継続検証できる。

## 3. 未完了・次にやること

### ユーザーの直近の要望: 「まちがいさがし」のイラスト化

現状の「まちがいさがし」は丸・四角・三角などの幾何学図形で差分を表現している。
ユーザーから、下記のような**手描き漫画タッチ＋ドット網掛けのプロ品質イラスト**
（ビーチのシーンなど、市販の間違い探し本のような絵）にしたいという要望があった。
参考画像はチャット添付のみで、このリポジトリには保存していない。

**制約の説明済み**: この環境（Claude Code）には画像生成AIのツールが無く、
参考画像のような線画イラストの自動生成はできないことをユーザーに伝え済み。

**代替案として提示し、ユーザーの最終GOは得ないまま「続きはChatGPTで」となった案**:
- OpenMoji等、**CC BY-SA（要クレジット表記）でSVG配布されている無料アイコン素材**を
  部品として使い、太陽・花・木・カニ・スイカ・紅葉・雪だるまなど「それらしいイラスト」を
  組み立てる（幾何学図形より視覚的に楽しく、まちがいさがしらしくなる）
- 月（`new Date().getMonth()`）に応じてアイコンセットを自動で季節替えする案:
  - 3〜5月: 桜・ちょうちょ 等
  - 6〜8月: ひまわり・スイカ・カニ 等
  - 9〜11月: 紅葉・きのこ 等
  - 12〜2月: 雪だるま・みかん 等
- 365日分を事前生成する代替案もユーザーから出ていたが、上記の「アイコン組み合わせで
  都度自動生成」の方が実装量が少なく、無限バリエーションも保てるため、そちらを提案していた
- **ここまでで実装は未着手**（アイコンの調達・ライセンス確認・埋め込み・季節分岐ロジックの
  追加はこれから）

### 実装時に触る箇所（`web/脳トレメーカー.html` 内）
- `SHAPE_KINDS` / `COLORS` / `drawShape()` — 現状の図形描画。
  **なかまはずれさがし側はこのままでよい**（ユーザーの要望は「まちがいさがし」のみ）
- `DIFF_DIFFICULTY` / `generateSpotDiff()` / `drawDiffPanel()` /
  `renderDiffSheets()` — まちがいさがし側のロジック。ここをイラスト版に差し替える
- 差し替える際も、既存の「色変更／サイズ変更／消失」という差分の出し方（`el.diff`の
  `["color", ...]` / `["size", ...]` / `["remove", null]`）の枠組みはそのまま流用できる設計
  になっている（アイコン描画関数を `drawShape` から `drawIllustration` のような関数に
  差し替えるだけで済むはず）

## 4. アーキテクチャメモ（HTML内部の構造）

`web/脳トレメーカー.html` は単一ファイルで、`<script>` 内は以下のセクション構成:
1. 共通ユーティリティ（`RNG`クラス＝mulberry32による再現可能な乱数、SVG生成ヘルパー）
2. 図形描画（`SHAPE_KINDS`, `COLORS`, `drawShape`, `markCircle`）
3. シート（用紙）組み立て共通ヘルパー（`buildSheet` — A4サイズのdiv生成、
   タイトル/日付名前欄/フッターを配置）
4. めいろ（`generateMaze`, `solveMaze`, `drawMazeWalls`, `renderMazeSheets`）
5. なかまはずれさがし（`ODD_DIFFICULTY`, `makeOddPuzzle`, `drawOddBox`, `renderOddSheets`）
6. まちがいさがし（`DIFF_DIFFICULTY`, `generateSpotDiff`, `drawDiffPanel`, `renderDiffSheets`）
7. UI配線（ボタンのイベントリスナー、`generateAndPrint()`が起点）

SVG座標系はmm単位（`viewBox="0 0 W H"` で1ユニット=1mm）を使っており、
最初に作ったPython/fpdf2版とほぼ1:1で座標ロジックを移植した経緯がある。

印刷用紙のレイアウトバジェット（ヘッダー分・フッター分の余白のマジックナンバー、
例: `s1.contentH - 28` など）は、実際にヘッドレスChromeで印刷PDFを出して
ラスタライズ→目視確認しながら調整した実測値。イラスト化などでレイアウトを変える際は、
同じ「PDF化→ラスタライズ→目視」の手順で余白の overflow / footerとの重なりがないか
再確認することを推奨する。

## 5. ローカル環境情報

- OS: macOS（darwin）
- プロジェクトパス: `~/brain-training-app`
- 本体: `~/brain-training-app/web/脳トレメーカー.html`
- git remote: `origin` = `https://github.com/youshengyinolai-tech/brain-training-app.git`
- GitHub CLI設定: `GH_CONFIG_DIR=~/.gh-config`（デフォルトの`~/.config/gh`は
  このマシンでroot所有・書き込み不可のため回避した）
