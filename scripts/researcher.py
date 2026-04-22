import os
import google.generativeai as genai

# 從 GitHub 設定中讀取 Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# 取得你寫在 Issue 裡的內容
issue_content = os.getenv("ISSUE_BODY")

# AI 的指令（Prompt）
prompt = f"你是一位專業技術研究員。請針對以下主題撰寫研究報告：{issue_content}"

response = model.generate_content(prompt)
print(response.text)
