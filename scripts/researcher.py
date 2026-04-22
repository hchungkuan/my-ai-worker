import os
import sys
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有提供研究主題")
    
    if not api_key:
        print("❌ 錯誤：GitHub Secret 中找不到 GEMINI_API_KEY")
        return

    # 建立 Client
    client = genai.Client(api_key=api_key)
    
    try:
        # 直接使用你在 AI Studio 看到的最新模型名稱
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=f"你是一位技術研究專家，請針對以下主題進行深入研究，並產出結構清晰的 Markdown 報告：\n\n{issue_text}"
        )
        
        if response.text:
            print(response.text)
        else:
            print("⚠️ AI 回傳內容為空，請檢查輸入內容。")
            
    except Exception as e:
        # 如果還是 429，我們會印出更友善的重試建議
        error_msg = str(e)
        if "429" in error_msg:
            print(f"### ⏳ AI 員工忙碌中 (429)\n原因：免費額度暫時用完，請等待 1 分鐘後再重新貼標籤測試。")
        else:
            print(f"### ❌ AI 員工執行失敗\n原因：`{error_msg}`")

if __name__ == "__main__":
    main()
