import os
import sys
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# --- 專業視覺參數 ---
VECTOR_BLUE = RGBColor(0, 51, 102)
TEXT_DARK = RGBColor(33, 33, 33)
FONT_MAIN = 'Microsoft JhengHei'

def clean_md_syntax(text):
    """🚀 核心優化 1：徹底清除 Markdown 殘留符號 (*, **, #)"""
    if not text:
        return ""
    # 移除粗體 **text** -> text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # 移除其餘單個 * 或 _
    text = text.replace('*', '').replace('_', '')
    # 移除標題符號 #
    text = text.replace('#', '').strip()
    return text

def set_title_style(title_shape, title_text):
    """🚀 核心優化 2：動態調整標題字體大小，防止溢出"""
    title_shape.text = title_text
    tf = title_shape.text_frame
    tf.word_wrap = True  # 開啟自動換行
    
    p = tf.paragraphs[0]
    p.font.name = FONT_MAIN
    p.font.bold = True
    p.font.color.rgb = VECTOR_BLUE
    
    # 根據標題長度動態調整字體大小
    char_count = len(title_text)
    if char_count > 30:
        p.font.size = Pt(20) # 標題超長
    elif char_count > 20:
        p.font.size = Pt(24) # 標題稍長
    else:
        p.font.size = Pt(30) # 標準長度

def add_slide_with_table(prs, title, table_data):
    """建立帶有美化表格的投影片"""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    set_title_style(slide.shapes.title, f"{title} - 硬體對應表")
    
    if not table_data: return

    rows = len(table_data)
    cols = len(table_data[0])
    
    left, top = Inches(0.5), Inches(1.5)
    width, height = Inches(9.0), Inches(0.6 * rows)
    
    shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = shape.table

    for r, row in enumerate(table_data):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            # 清洗表格內的文字
            cell.text = clean_md_syntax(cell_text)
            
            # 表格標題樣式
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = VECTOR_BLUE
                for p in cell.text_frame.paragraphs:
                    p.font.color.rgb = RGBColor(255, 255, 255)
                    p.font.bold = True
                    p.font.size = Pt(11)
                    p.font.name = FONT_MAIN
            else:
                for p in cell.text_frame.paragraphs:
                    p.font.size = Pt(10)
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
        nonlocal current_bullets, current_table
        if current_bullets:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            set_title_style(slide.shapes.title, current_slide_title)
            
            tf = slide.placeholders[1].text_frame
            tf.word_wrap = True
            for b in current_bullets:
                p = tf.add_paragraph()
                p.text = clean_md_syntax(b) # 清洗內容中的 *
                p.font.size = Pt(18)
                p.font.name = FONT_MAIN
                p.space_after = Pt(8)
            current_bullets = []
            
        if current_table:
            add_slide_with_table(prs, current_slide_title, current_table)
            current_table = []

    # --- 標題首頁 ---
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    # 首頁大標題也可以清洗
    slide.shapes.title.text = "Vector Informatik\n充電通訊協議與硬體對應研究"
    slide.placeholders[1].text = f"技術專家報告\n日期：{time.strftime('%Y-%m-%d')}"

    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'): continue

        if line.startswith('## '):
            flush_content()
            current_slide_title = clean_md_syntax(line)
            
        elif line.startswith('### '):
            flush_content()
            sub_title = clean_md_syntax(line)
            current_slide_title = f"{current_slide_title} - {sub_title}"

        elif line.startswith('|'):
            if '---' in line: continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells: current_table.append(cells)

        elif line.startswith(('* ', '- ', '1. ', '2. ')):
            current_bullets.append(line)
        
        elif len(line) > 5 and not line.startswith('|'):
            current_bullets.append(line)

    flush_content()
    prs.save(output_file)
    print(f"✅ 優化版 PPT 已產生：{output_file}")

import time
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "reports/report_001.md"
    create_pptx_from_md(target)
