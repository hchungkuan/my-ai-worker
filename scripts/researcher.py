import os
import sys
from google import genai  # 2026 新版 SDK 導入方式

def run():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("錯誤：找不到 GEMINI_API_KEY")
        sys.exit(1)

    # 初始化 Client
    client = genai.Client(api_key=api_key)
    
    # 取得 Issue 內容
    issue_body = os.environ.get("ISSUE_BODY", "請幫我做技術研究")
    
    try:
        # 使用最新 2.0 模型
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=issue_body
        )
        print(response.text)
    except Exception as e:
        print(f"API 調用失敗：{e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
