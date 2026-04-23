import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# --- 設定 Vector 企業風格色彩 ---
VECTOR_BLUE = RGBColor(0, 51, 102)
TEXT_BLACK = RGBColor(33, 33, 33)
FONT_NAME = 'Microsoft JhengHei'

def add_table_to_slide(slide, table_data):
    """將 Markdown 表格數據轉換為 PPT 實體表格"""
    if not table_data:
        return
    
    rows = len(table_data)
    cols = len(table_data[0])
    
    # 在投影片下方位置建立表格
    left = Inches(0.5)
    top = Inches(2.5)
    width = Inches(9.0)
    height = Inches(0.5 * rows)
    
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    for r, row_data in enumerate(table_data):
        for c, cell_text in enumerate(row_data):
            cell = table.cell(r, c)
            cell.text = cell_text.strip()
            # 設定表格字體
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(12)
                paragraph.font.name = FONT_NAME
                if r == 0: # 標題列加粗
                    paragraph.font.bold = True

def create_pptx_from_file(input_file="report.md", output_file="Vector_Presentation.pptx"):
    if not os.path.exists(input_file):
        print(f"❌ 找不到輸入檔案: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    prs = Presentation()

    # --- 處理投影片分割 ---
    # 先過濾掉 Markdown 的分隔線 ---
    content = content.replace('\n---', '')
    sections = content.split('Slide:')
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        lines = [l.strip() for l in section.strip().split('\n') if l.strip()]
        title_text = lines[0].replace('#', '').strip()
        
        # 區分列表內容與表格內容
        bullets = []
        table_data = []
        is_table = False
        
        for line in lines[1:]:
            if line.startswith('|'):
                # 排除 Markdown 表格的分隔線 |---|---|
                if '---' in line: continue
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells: table_data.append(cells)
            elif line.startswith('-'):
                bullets.append(line.lstrip('-').strip())

        # 選擇版面：第一張用標題版面，其餘用內容版面
        layout_idx = 0 if i == 1 else 1
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        
        # 設定標題
        title_shape = slide.shapes.title
        title_shape.text = title_text
        for p in title_shape.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.bold = True
            p.font.color.rgb = VECTOR_BLUE
            p.font.size = Pt(28)

        # 設定內容 (如果是標題頁)
        if layout_idx == 0:
            if len(lines) > 1:
                slide.placeholders[1].text = "\n".join(bullets)
        else:
            # 設定列表
            if bullets:
                body_shape = slide.placeholders[1]
                tf = body_shape.text_frame
                tf.word_wrap = True
                for b in bullets:
                    p = tf.add_paragraph()
                    p.text = b
                    p.font.size = Pt(18)
                    p.font.name = FONT_NAME
                    p.space_after = Pt(10)
            
            # 🚀 插入表格 (如果有的話)
            if table_data:
                add_table_to_slide(slide, table_data)

    prs.save(output_file)
    print(f"✅ PPTX 已產生: {output_file}")

if __name__ == "__main__":
    # 1. 檢查有沒有輸入參數
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # 2. 如果沒輸入，自動尋找目錄下最新的 .md 檔案，或者給予預設值
        print("💡 提示：未指定檔案，預設讀取 report.md")
        target_file = "report.md"

    # 3. 檢查檔案是否存在
    if os.path.exists(target_file):
        create_pptx_from_file(target_file)
    else:
        print(f"❌ 錯誤：找不到檔案 '{target_file}'，請確認檔名是否正確。")
