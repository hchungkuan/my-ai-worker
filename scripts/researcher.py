import os
import time
from google import genai  # 升級到最新的庫

def run_research():
    # 初始化客戶端
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    issue_content = os.getenv("ISSUE_BODY", "無內容")
    prompt = f"你是一位專業技術研究員。請針對以下主題撰寫研究報告：{issue_content}"

    try:
        # 使用最新 2.0 模型
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        print(response.text)
    except Exception as e:
        print(f"發生錯誤：{e}")
        # 如果是額度問題，等待 10 秒後再試一次（僅限自動化時）
        time.sleep(10)

if __name__ == "__main__":
    run_research()
