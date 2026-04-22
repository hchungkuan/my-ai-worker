import os
import sys
from google import genai

def main():
    # 1. 檢查變數
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "No content found.")
    
    if not api_key:
        print("❌ 錯誤：找不到 GEMINI_API_KEY Secret", file=sys.stderr)
        sys.exit(1)

    print(f"📡 正在嘗試連線 Gemini API... 研究主題：{issue_text[:20]}...", file=sys.stderr)

    # 2. 建立客戶端
    client = genai.Client(api_key=api_key)
    
    try:
        # 3. 嘗試調用模型 (加上簡單的重試邏輯)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"你是一位技術研究員，請研究並用 Markdown 回覆：{issue_text}"
        )
        
        if response.text:
            print(response.text) # 成功的話，這行會進到 report.md
        else:
            print("⚠️ AI 回傳了空內容", file=sys.stderr)
            
    except Exception as e:
        # 這裡會把真正的錯誤印出來，讓你在 GitHub Actions 畫面上直接看到
        print(f"❌ API 執行失敗！詳細原因：\n{str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
