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
    
    # 定義嘗試順序：先用 2.5，不行就換 2.0
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
    
    last_error = ""

    for model_name in models_to_try:
        try:
            print(f"📡 嘗試使用模型：{model_name}...", file=sys.stderr)
            
            response = client.models.generate_content(
                model=model_name, 
                contents=f"你是一位技術研究專家，請針對以下主題進行深入研究並產出 Markdown 報告：\n\n{issue_text}"
            )
            
            if response.text:
                # 成功！印出報告內容
                print(response.text)
                return 
            
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ {model_name} 暫時無法使用，原因：{last_error}", file=sys.stderr)
            # 等待 2 秒後嘗試下一個模型
            time.sleep(2)
            continue

    # 如果所有模型都失敗了
    print(f"### ❌ AI 員工全線忙碌中\n")
    print(f"嘗試了 {models_to_try} 都失敗了。最後一個錯誤訊息：\n`{last_error}`")
    print(f"\n*建議：請過幾分鐘後再重新貼標籤測試。*")

if __name__ == "__main__":
    main()
