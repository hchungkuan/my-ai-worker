import os
import sys
import time
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_text = os.environ.get("ISSUE_BODY", "沒有研究主題")
    
    if not api_key:
        print("❌ 錯誤：找不到 API KEY")
        return

    client = genai.Client(api_key=api_key)
    
    max_attempts = 3
    # 設定基礎等待時間（秒）
    base_delay = 20 

    for i in range(max_attempts):
        try:
            print(f"📡 第 {i+1} 次嘗試啟動 AI 員工 (使用 Gemini 2.5 Flash)...", file=sys.stderr)
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=f"你是一位技術研究專家，請針對以下主題產出詳細的 Markdown 報告：\n\n{issue_text}"
            )
            
            if response.text:
                print(response.text)
                return # 成功就收工
            
        except Exception as e:
            error_msg = str(e)
            # 如果還沒到最後一次嘗試，就進行等待
            if i < max_attempts - 1:
                # 計算等待時間：20s, 40s, 80s... 每次加倍
                wait_time = base_delay * (2 ** i)
                print(f"⚠️ 嘗試失敗，原因：{error_msg[:100]}...", file=sys.stderr)
                print(f"⏳ 等待 {wait_time} 秒後進行下一次重試...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                # 最後一次也失敗了
                print(f"### ❌ AI 員工在 3 次重試後仍然失敗\n")
                print(f"最後一次錯誤訊息：\n`{error_msg}`")
                print(f"\n*建議：這通常代表您的 Google AI 專案配額目前為 0。請確認是否已在 AI Studio 建立『新專案』的金鑰。*")

if __name__ == "__main__":
    main()
