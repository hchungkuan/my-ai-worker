import os
import sys
import time
from google import genai
from pptx import Presentation  # 確保 Workflow 中有 pip install python-pptx

def create_pptx_from_text(text, filename="Vector_Research.pptx"):
    """將 AI 輸出的結構化文字轉為 PPTX 檔案"""
    prs = Presentation()
    # 分割投影片內容
    sections = text.split('Slide:')
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        title_text = lines[0].strip()
        bullet_points = lines[1:]
        
        # 加入一張標題+內容的投影片
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title_text
        
        if bullet_points:
            tf = slide.placeholders[1].text_frame
            for point in bullet_points:
                clean_point = point.strip().lstrip('-').strip()
                if clean_point:
                    p = tf.add_paragraph()
                    p.text = clean_point
    
    prs.save(filename)
    print(f"✅ 成功產生 PPT 檔案：{filename}", file=sys.stderr)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有研究主題")
    # 🚀 讀取來自 GitHub Workflow 的標籤名稱
    label = os.environ.get("TRIGGER_LABEL", "research")
    
    if not api_key:
        print("❌ 錯誤：找不到 API KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # 🧠 根據標籤切換 Prompt 與身份
    if label == "presentation":
        system_instruction = "你是一位專業的技術簡報製作師。"
        prompt = f"""
        請針對以下主題製作 PPT 結構，直接以文字格式輸出。
        格式要求：
        Slide: [投影片標題]
        - [重點 1]
        - [重點 2]

        主題：{issue_text}
        """
    else:
        system_instruction = "你是一位專精於 Vector Informatik 與 EV 充電標準的技術研究專家。"
        prompt = f"請針對以下主題產出詳細的 Markdown 技術研究報告：\n\n{issue_text}"

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
                # 1. 印出文字結果 (這會發佈在 Issue 留言)
                print(response.text)
                
                # 2. 🚀 如果是簡報標籤，則額外製作 PPT 檔案
                if label == "presentation":
                    create_pptx_from_text(response.text)
                
                return # 成功就收工
            
        except Exception as e:
            error_msg = str(e)
            if i < max_attempts - 1:
                wait_time = base_delay * (2 ** i)
                print(f"⚠️ 嘗試失敗：{error_msg[:100]}...", file=sys.stderr)
                print(f"⏳ 等待 {wait_time} 秒後重試...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                print(f"### ❌ AI 員工在 3 次重試後仍然失敗\n最後錯誤訊息：`{error_msg}`")

if __name__ == "__main__":
    main()
