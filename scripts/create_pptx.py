import os
import sys
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# --- 專業視覺參數 ---
VECTOR_BLUE = RGBColor(0, 51, 102)  # Vector 標誌深藍
TEXT_DARK = RGBColor(33, 33, 33)
BG_LIGHT = RGBColor(245, 245, 245)
FONT_MAIN = 'Microsoft JhengHei'

def set_cell_font(cell, size=Pt(12), bold=False):
    """設定表格單元格字體"""
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.name = FONT_NAME
        paragraph.font.size = size
        paragraph.font.bold = bold
        paragraph.font.color.rgb = TEXT_DARK

def add_slide_with_table(prs, title, table_data):
    """為表格內容獨立建立一張投影片"""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = f"{title} - 硬體對應"
    
    # 設定標題樣式
    title_para = slide.shapes.title.text_frame.paragraphs[0]
    title_para.font.color.rgb = VECTOR_BLUE
    title_para.font.name = FONT_MAIN

    if not table_data: return

    rows = len(table_data)
    cols = len(table_data[0])
    
    # 計算表格位置 (居中且佔滿寬度)
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9.0)
    height = Inches(0.6 * rows)
    
    shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = shape.table

    for r, row in enumerate(table_data):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = cell_text.strip()
            # 表格標題行美化
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = VECTOR_BLUE
                for p in cell.text_frame.paragraphs:
                    p.font.color.rgb = RGBColor(255, 255, 255)
                    p.font.bold = True
                    p.font.size = Pt(12)
            else:
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(11)
                    p.font.name = FONT_MAIN

def create_pptx_from_md(md_file="report.md", output_file="Vector_Presentation.pptx"):
    if not os.path.exists(md_file):
        print(f"❌ 錯誤：找不到 {md_file}")
        return

    prs = Presentation()
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_slide_title = "Vector 技術研究"
    current_bullets = []
    current_table = []
    
    def flush_content():
        """將目前暫存的內容寫入投影片並清空"""
        nonlocal current_bullets, current_table
        if current_bullets:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = current_slide_title
            # 設定標題字體
            title_para = slide.shapes.title.text_frame.paragraphs[0]
            title_para.font.color.rgb = VECTOR_BLUE
            title_para.font.name = FONT_MAIN
            
            tf = slide.placeholders[1].text_frame
            tf.word_wrap = True
            for b in current_bullets:
                p = tf.add_paragraph()
                p.text = b
                p.font.size = Pt(18)
                p.font.name = FONT_MAIN
                p.space_after = Pt(10)
            current_bullets = []
            
        if current_table:
            add_slide_with_table(prs, current_slide_title, current_table)
            current_table = []

    # --- 標題首頁 ---
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Vector Informatik\n充電通訊協議與硬體對應研究"
    slide.placeholders[1].text = f"技術專家報告\n日期：{os.path.getmtime(md_file)}"

    # --- 解析 Markdown ---
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'): continue

        # 1. 偵測大標題 (協定名稱) -> 重設標題
        if line.startswith('## '):
            flush_content()
            current_slide_title = line.replace('## ', '').replace('協定名稱：', '').strip()
            
        # 2. 偵測小標題 (描述、對應表、門檻) -> 強制換頁
        elif line.startswith('### '):
            flush_content()
            sub_title = line.replace('### ', '').strip()
            current_slide_title = f"{current_slide_title} - {sub_title}"

        # 3. 偵測表格行
        elif line.startswith('|'):
            if '---' in line: continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells: current_table.append(cells)

        # 4. 偵測清單
        elif line.startswith(('* ', '- ', '1. ', '2. ')):
            clean_bullet = re.sub(r'^(\*|-|\d+\.)\s+', '', line)
            current_bullets.append(clean_bullet)
        
        # 5. 一般段落文字
        elif len(line) > 5 and not line.startswith('|'):
            current_bullets.append(line)

    flush_content() # 處理最後殘留內容
    prs.save(output_file)
    print(f"✅ 專業 PPT 已產生：{output_file}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "reports/report_001.md"
    create_pptx_from_md(target)
