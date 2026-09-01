"""脳トレメーカー - 職員向けのシンプルな操作画面。"""

import random
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

from .maze import render_maze_pdf
from .odd_one_out import render_odd_one_out_pdf
from .pdf_common import BrainTrainPDF
from .spot_diff import render_spot_diff_pdf
from .storage import get_output_dir, make_output_path, open_path

DIFFICULTIES = ["やさしい", "ふつう", "むずかしい"]

JP_FONT_CANDIDATES = ["Yu Gothic UI", "Meiryo UI", "Meiryo", "Hiragino Sans", "TkDefaultFont"]


def _pick_font_family(root):
    available = set(tkfont.families(root))
    for name in JP_FONT_CANDIDATES:
        if name in available:
            return name
    return "TkDefaultFont"


class BrainTrainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("脳トレメーカー")
        self.geometry("880x700")
        self.minsize(760, 620)
        self.configure(bg="#f4f5f7")

        family = _pick_font_family(self)
        self.f_title = tkfont.Font(family=family, size=30, weight="bold")
        self.f_section = tkfont.Font(family=family, size=15, weight="bold")
        self.f_button = tkfont.Font(family=family, size=18, weight="bold")
        self.f_button_big = tkfont.Font(family=family, size=22, weight="bold")
        self.f_normal = tkfont.Font(family=family, size=13)
        self.f_status = tkfont.Font(family=family, size=13)

        self.difficulty_var = tk.StringVar(value="ふつう")
        self.answer_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="ボタンをおすと、あたらしい教材ができます。")

        self._build_layout()

    # ------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self, bg="#f4f5f7")
        header.pack(fill="x", padx=30, pady=(24, 8))
        tk.Label(
            header, text="脳トレメーカー", font=self.f_title, bg="#f4f5f7", fg="#222"
        ).pack(anchor="w")
        tk.Label(
            header,
            text="ボタンをおすたびに、あたらしい問題ができます。印刷してお使いください。",
            font=self.f_normal,
            bg="#f4f5f7",
            fg="#555",
        ).pack(anchor="w", pady=(4, 0))

        # 難易度選択
        diff_frame = tk.Frame(self, bg="#f4f5f7")
        diff_frame.pack(fill="x", padx=30, pady=(14, 4))
        tk.Label(
            diff_frame, text="むずかしさ", font=self.f_section, bg="#f4f5f7", fg="#333"
        ).pack(anchor="w")
        btn_row = tk.Frame(diff_frame, bg="#f4f5f7")
        btn_row.pack(fill="x", pady=(6, 0))
        for level in DIFFICULTIES:
            b = tk.Radiobutton(
                btn_row,
                text=level,
                variable=self.difficulty_var,
                value=level,
                indicatoron=False,
                font=self.f_button,
                width=10,
                pady=10,
                bg="#ffffff",
                selectcolor="#cfe3ff",
                activebackground="#e6f0ff",
                relief="raised",
                bd=2,
            )
            b.pack(side="left", padx=(0, 10))

        # こたえページ
        ans_frame = tk.Frame(self, bg="#f4f5f7")
        ans_frame.pack(fill="x", padx=30, pady=(14, 4))
        tk.Checkbutton(
            ans_frame,
            text="こたえのページも印刷する(職員用)",
            variable=self.answer_var,
            font=self.f_normal,
            bg="#f4f5f7",
            activebackground="#f4f5f7",
        ).pack(anchor="w")

        # メインボタン
        main_frame = tk.Frame(self, bg="#f4f5f7")
        main_frame.pack(fill="x", padx=30, pady=(18, 6))
        tk.Label(
            main_frame, text="今日の脳トレを作る", font=self.f_section, bg="#f4f5f7", fg="#333"
        ).pack(anchor="w")
        tk.Button(
            main_frame,
            text="全部まとめて1つ作る（めいろ＋なかまはずれ＋まちがいさがし）",
            font=self.f_button_big,
            bg="#2f6fed",
            fg="white",
            activebackground="#255bc4",
            activeforeground="white",
            relief="flat",
            pady=18,
            command=lambda: self.generate("all"),
        ).pack(fill="x", pady=(8, 0))

        # 個別ボタン
        indiv_frame = tk.Frame(self, bg="#f4f5f7")
        indiv_frame.pack(fill="x", padx=30, pady=(20, 6))
        tk.Label(
            indiv_frame, text="1種類だけ作る", font=self.f_section, bg="#f4f5f7", fg="#333"
        ).pack(anchor="w")

        grid = tk.Frame(indiv_frame, bg="#f4f5f7")
        grid.pack(fill="x", pady=(8, 0))
        grid.columnconfigure((0, 1, 2), weight=1)

        specs = [
            ("めいろ", "maze", "#2ca058"),
            ("なかまはずれさがし", "odd", "#e08a1e"),
            ("まちがいさがし", "diff", "#c14f4f"),
        ]
        for col, (label, kind, color) in enumerate(specs):
            tk.Button(
                grid,
                text=label,
                font=self.f_button,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                pady=16,
                command=lambda k=kind: self.generate(k),
            ).grid(row=0, column=col, sticky="ew", padx=6)

        # ステータス表示
        status_frame = tk.Frame(self, bg="#eef1f5", bd=1, relief="solid")
        status_frame.pack(fill="x", padx=30, pady=(24, 6))
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=self.f_status,
            bg="#eef1f5",
            fg="#222",
            anchor="w",
            justify="left",
            wraplength=780,
            padx=14,
            pady=12,
        ).pack(fill="x")

        # フッター
        footer = tk.Frame(self, bg="#f4f5f7")
        footer.pack(fill="x", padx=30, pady=(4, 20), side="bottom")
        tk.Button(
            footer,
            text="保存先フォルダを開く",
            font=self.f_normal,
            command=self.open_output_folder,
            relief="flat",
            bg="#dde2ea",
            padx=10,
            pady=6,
        ).pack(side="left")
        tk.Label(
            footer,
            text=f"保存先: {get_output_dir()}",
            font=self.f_normal,
            bg="#f4f5f7",
            fg="#777",
        ).pack(side="left", padx=12)

    # ------------------------------------------------------------------
    def generate(self, kind):
        difficulty = self.difficulty_var.get()
        include_answer = self.answer_var.get()
        rng = random.Random()

        labels = {
            "all": "今日の脳トレ",
            "maze": "めいろ",
            "odd": "なかまはずれさがし",
            "diff": "まちがいさがし",
        }
        label = labels[kind]
        self.status_var.set("作成中です。少々お待ちください…")
        self.update_idletasks()

        try:
            pdf = BrainTrainPDF()
            if kind == "all":
                render_maze_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)
                render_odd_one_out_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)
                render_spot_diff_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)
            elif kind == "maze":
                render_maze_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)
            elif kind == "odd":
                render_odd_one_out_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)
            elif kind == "diff":
                render_spot_diff_pdf(pdf, difficulty, rng=rng, include_answer=include_answer)

            path = make_output_path(label)
            pdf.output(str(path))
            open_path(path)
            self.status_var.set(f"「{label}」を作成しました。印刷画面が開きます。\nファイル: {path.name}")
        except Exception as e:  # noqa: BLE001 - 職員に分かりやすく伝える
            self.status_var.set("作成中にエラーが発生しました。もう一度お試しください。")
            messagebox.showerror("エラー", f"教材の作成中にエラーが発生しました。\n\n詳細: {e}")

    def open_output_folder(self):
        open_path(get_output_dir())


def main():
    app = BrainTrainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
