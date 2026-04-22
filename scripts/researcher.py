import os
import sys
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有提供研究主題")
    
    if not api_key:
        print("❌ 錯誤：GitHub Secret 中找不到 GEMINI_API_KEY")
        return

    # 初始化 Client
    client = genai.Client(api_key=api_key)
    
    try:
        # 在 2026 年，直接使用 'gemini-1.5-flash' 或 'models/gemini-2.0-flash'
        # 我們這裡採用最標準的簡寫
        response = client.models.generate_content(
        model='gemini-2.0-flash', 
        contents=f"請針對以下主題進行研究：\n\n{issue_text}"
        )
        
        if response.text:
            print(response.text)
        else:
            print("⚠️ AI 回傳了空內容。")
            
    except Exception as e:
        # 這次如果出錯，我們會印出更詳細的資訊
        print(f"### ❌ AI 員工執行失敗\n原因：`{str(e)}`\n\n*提示：請檢查 Google AI Studio 中的模型權限。*")

if __name__ == "__main__":
    main()
