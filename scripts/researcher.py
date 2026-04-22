import os
import sys
# 注意：這裡就是 2026 年最新的導入方式
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "No content found.")
    
    if not api_key:
        print("Error: GEMINI_API_KEY is missing.")
        sys.exit(1)

    # 建立客戶端
    client = genai.Client(api_key=api_key)
    
    try:
        # 使用最新 2.0 模型進行研究
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"請針對以下技術主題進行深入研究並寫出 Markdown 報告：\n\n{issue_text}"
        )
        # 把結果印出來，GitHub Actions 會把它存進 report.md
        print(response.text)
    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
