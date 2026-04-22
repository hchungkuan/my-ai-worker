import os
import sys
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有提供研究主題")
    
    if not api_key:
        print("❌ 錯誤：GitHub Secret 中找不到 GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    
    try:
        # 💡 如果 2.0-flash 還是報 Quota 錯誤，可以試著改成 'gemini-1.5-flash'
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"請針對以下技術主題進行深入研究並寫出 Markdown 報告：\n\n{issue_text}"
        )
        
        if response.text:
            print(response.text)
        else:
            print("⚠️ AI 回傳了空內容，請檢查 Prompt 指令。")
            
    except Exception as e:
        # 這裡的錯誤訊息會直接被寫入 report.md，讓你在 Issue 看到
        print(f"### ❌ AI 員工執行失敗\n原因：`{str(e)}`")

if __name__ == "__main__":
    main()
