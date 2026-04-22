import os
import sys
import time
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有主題")
    
    if not api_key:
        print("❌ 錯誤：找不到 API KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # 嘗試次數
    attempts = 3
    for i in range(attempts):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=f"請針對以下主題進行研究並產出 Markdown 報告：\n\n{issue_text}"
            )
            print(response.text)
            return  # 成功後直接退出
            
        except Exception as e:
            if "503" in str(e) and i < attempts - 1:
                print(f"### ⏳ 伺服器忙碌中，{i+1} 秒後重試...", file=sys.stderr)
                time.sleep(5)  # 等待 5 秒再試
                continue
            else:
                print(f"### ❌ AI 員工執行失敗\n原因：`{str(e)}`")
                break

if __name__ == "__main__":
    main()
