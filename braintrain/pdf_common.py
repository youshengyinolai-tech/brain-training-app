"""共通のPDF基盤クラス。日本語フォントの読み込みと、
すべての教材で共通のヘッダー・フッター・タイトル表示を行う。"""

import os
import sys
from datetime import date

from fpdf import FPDF

PAGE_W_MM = 210.0
PAGE_H_MM = 297.0
MARGIN_MM = 15.0


def resource_path(*parts):
    """開発時・PyInstaller onefile 実行時のどちらでも同梱リソースを見つける。"""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


class BrainTrainPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.set_margins(MARGIN_MM, MARGIN_MM, MARGIN_MM)
        regular = resource_path("assets", "fonts", "NotoSansJP-Regular.ttf")
        bold = resource_path("assets", "fonts", "NotoSansJP-Bold.ttf")
        self.add_font("NotoJP", "", regular)
        self.add_font("NotoJP", "B", bold)
        self.set_font("NotoJP", "", 11)
        self._page_title = ""

    def start_worksheet_page(self, title, subtitle="", show_name_date=True, answer_page=False):
        """1ページ分の教材ページを開始し、タイトル欄を描画する。
        戻り値: 本文を描画してよい領域の (x, y, w, h)。
        """
        self.add_page()
        self._page_title = title

        self.set_font("NotoJP", "B", 20)
        self.set_xy(MARGIN_MM, MARGIN_MM)
        header_text = title + ("(こたえ)" if answer_page else "")
        self.cell(0, 12, header_text, align="L")

        if subtitle:
            self.set_font("NotoJP", "", 12)
            self.set_xy(MARGIN_MM, MARGIN_MM + 11)
            self.cell(0, 8, subtitle, align="L")

        top_used = MARGIN_MM + 11 + (8 if subtitle else 0)

        if show_name_date and not answer_page:
            self.set_font("NotoJP", "", 12)
            name_date_y = MARGIN_MM
            box_w = 75
            box_x = PAGE_W_MM - MARGIN_MM - box_w
            self.set_xy(box_x, name_date_y)
            self.cell(box_w, 8, "日付：　　　月　　　日", align="R")
            self.set_xy(box_x, name_date_y + 8)
            self.cell(box_w, 8, "名前：", align="R")

        content_y = top_used + 6
        content_h = PAGE_H_MM - MARGIN_MM - content_y - 10
        content_w = PAGE_W_MM - 2 * MARGIN_MM
        self._draw_footer()
        return MARGIN_MM, content_y, content_w, content_h

    def _draw_footer(self):
        self.set_font("NotoJP", "", 9)
        self.set_text_color(140, 140, 140)
        self.set_xy(MARGIN_MM, PAGE_H_MM - MARGIN_MM + 2)
        self.cell(PAGE_W_MM - 2 * MARGIN_MM, 6, "脳トレメーカー", align="L")
        self.set_xy(MARGIN_MM, PAGE_H_MM - MARGIN_MM + 2)
        self.cell(PAGE_W_MM - 2 * MARGIN_MM, 6, str(date.today()), align="R")
        self.set_text_color(0, 0, 0)

    def draw_frame(self, x, y, w, h):
        self.set_draw_color(60, 60, 60)
        self.set_line_width(0.6)
        self.rect(x, y, w, h, style="D")
