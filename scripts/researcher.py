import os
import sys
import time
from google import genai
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_pptx_from_text(text, title_context, filename="Technical_Research.pptx"):
    """將 AI 輸出的結構化文字轉為美化後的 PPTX 檔案"""
    prs = Presentation()
    
    # --- 1. 加入總標題首頁 ---
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title_shape = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    # 使用 Issue 標題作為簡報標題
    title_shape.text = f"{title_context} 技術研究報告"
    subtitle.text = f"由 AI 技術助理自動生成\n日期：{time.strftime('%Y-%m-%d')}"
    
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                paragraph.font.name = 'Microsoft JhengHei'
                paragraph.font.bold = True

    # --- 2. 處理內容投影片 ---
    sections = text.split('Slide:')
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        title_text = lines[0].strip()
        bullet_points = lines[1:]
        
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        # 標題格式 (保持專業藍色調，但不寫死品牌名)
        title_shape = slide.shapes.title
        title_shape.text = title_text
        title_frame = title_shape.text_frame
        for p in title_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(28) # 稍微縮小以適應長標題
            p.font.name = 'Microsoft JhengHei'
            p.font.color.rgb = RGBColor(0, 51, 102) 

        if bullet_points:
            body_shape = slide.placeholders[1]
            tf = body_shape.text_frame
            tf.word_wrap = True
            
            for point in bullet_points:
                clean_point = point.strip().lstrip('-').lstrip('*').strip()
                if clean_point:
                    p = tf.add_paragraph()
                    p.text = clean_point
                    p.font.size = Pt(20)
                    p.font.name = 'Microsoft JhengHei'
                    p.space_after = Pt(12)
                    p.level = 0
    
    prs.save(filename)
    print(f"✅ 成功產生技術報告 PPT：{filename}", file=sys.stderr)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_title = os.environ.get("ISSUE_TITLE", "技術研究主題") # 🚀 新增：讀取 Issue 標題
    issue_body = os.environ.get("ISSUE_BODY", "未提供詳細內容")
    label = os.environ.get("TRIGGER_LABEL", "research")
    
    if not api_key:
        print("❌ 錯誤：找不到 API KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # 🧠 根據標籤切換通用的技術專家身份
    if label == "presentation":
        system_instruction = "你是一位資深的技術諮詢顧問，擅長分析複雜技術架構並製作專業的簡報結構。"
        prompt = f"""
        請針對主題【{issue_title}】製作 PPT 結構。
        
        【內容要求】：
        1. 議程 (Agenda)：列出研究關鍵章節。
        2. 技術背景與現狀：說明此技術的核心標準與發展。
        3. 核心解決方案：找出與此主題相關的主流硬體設備或軟體工具。
        4. 技術挑戰分析：分析實作中的難點與關鍵技術門檻。
        5. 總結與未來展望。

        【格式規範】：
        每張投影片以 'Slide:' 開頭。內容精煉，適合簡報呈現。
        
        主題內容：{issue_body}
        """
    else:
        system_instruction = "你是一位專精於技術標準、系統開發與產業分析的研究專家。"
        prompt = f"請針對【{issue_title}】產出詳細的 Markdown 技術研究報告。內容需包含技術定義、對應硬體/工具、與深度技術門檻分析：\n\n{issue_body}"

    max_attempts = 3
    base_delay = 20 

    for i in range(max_attempts):
        try:
            print(f"📡 第 {i+1} 次嘗試 ({label} 模式)...", file=sys.stderr)
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=f"{system_instruction}\n\n{prompt}"
            )
            
            if response.text:
                print(response.text)
                if label == "presentation":
                    # 傳入 issue_title 作為 PPT 的動態標題
                    create_pptx_from_text(response.text, issue_title)
                return 
            
        except Exception as e:
            error_msg = str(e)
            if i < max_attempts - 1:
                wait_time = base_delay * (2 ** i)
                print(f"⚠️ 失敗：{error_msg[:100]}... 等待重試", file=sys.stderr)
                time.sleep(wait_time)
            else:
                print(f"### ❌ AI 員工執行失敗\n最後錯誤訊息：`{error_msg}`")

if __name__ == "__main__":
    main()
