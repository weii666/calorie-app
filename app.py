"""
食物熱量估算 App
----------------
使用者上傳一張照片，透過 Google Gemini 視覺模型：
  - 若照片為食物：回傳食物名稱與大概熱量（kcal）
  - 若照片不是食物：回傳「這個不是食物」
"""

import json
import os

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

# Gemini 視覺模型；flash 版本速度快、成本低，足以應付此任務。
# 使用 -latest 別名，讓程式自動跟隨 Google 當前的穩定 flash 模型，不會因版本下架而失效。
MODEL_NAME = "gemini-flash-latest"

NOT_FOOD_MESSAGE = "這個不是食物"

# 要求模型以固定 JSON 結構回覆，方便程式判斷
PROMPT = """你是一位營養師。請仔細分析這張照片。

請只用 JSON 格式回覆，不要有其他文字，結構如下：
{
  "is_food": true 或 false,
  "food_name": "食物名稱（繁體中文），若不是食物則為空字串",
  "calories": 估算的總熱量整數（kcal），若不是食物則為 0,
  "note": "簡短的說明或估算依據（繁體中文），若不是食物則為空字串"
}

判斷規則：
- 只要照片主體是可食用的食物或飲料，is_food 就是 true。
- 若照片主體不是食物（例如風景、人物、物品、動物等），is_food 為 false。
- calories 請以照片中看到的份量為基礎做合理估算。
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "is_food": {"type": "boolean"},
        "food_name": {"type": "string"},
        "calories": {"type": "integer"},
        "note": {"type": "string"},
    },
    "required": ["is_food", "food_name", "calories", "note"],
}


def _get_client() -> genai.Client:
    """建立 Gemini client，若沒有 API key 則丟出易懂的錯誤。"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise gr.Error(
            "找不到 GOOGLE_API_KEY。請在本機的 .env 檔設定，"
            "或在 Cloud Run 服務以環境變數／Secret 的方式設定 GOOGLE_API_KEY。"
        )
    return genai.Client(api_key=api_key)


def analyze_image(image: Image.Image) -> str:
    """分析圖片並回傳給使用者看的文字結果。"""
    if image is None:
        return "請先上傳一張照片。"

    client = _get_client()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[PROMPT, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.2,
            ),
        )
    except Exception as exc:  # 網路 / 金鑰 / 配額等錯誤
        raise gr.Error(f"呼叫 Gemini 失敗：{exc}") from exc

    try:
        data = json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        # 萬一模型沒有回傳合法 JSON，退回原始文字
        return response.text or "無法解析模型回覆，請再試一次。"

    if not data.get("is_food"):
        return NOT_FOOD_MESSAGE

    food_name = data.get("food_name") or "未知食物"
    calories = data.get("calories", 0)
    note = data.get("note", "")

    result = f"🍽️ 食物：{food_name}\n🔥 大概熱量：約 {calories} kcal"
    if note:
        result += f"\n📝 說明：{note}"
    result += "\n\n⚠️ 熱量為 AI 依照片估算，僅供參考。"
    return result


with gr.Blocks(title="食物熱量估算") as demo:
    gr.Markdown(
        "# 🍱 食物熱量估算\n"
        "上傳一張照片，AI 會告訴你食物的大概熱量。"
        "如果照片不是食物，會回覆「這個不是食物」。"
    )
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="上傳食物照片")
            analyze_btn = gr.Button("估算熱量", variant="primary")
        with gr.Column():
            output = gr.Textbox(label="結果", lines=8)

    analyze_btn.click(fn=analyze_image, inputs=image_input, outputs=output)
    image_input.upload(fn=analyze_image, inputs=image_input, outputs=output)


if __name__ == "__main__":
    # Cloud Run（及多數雲端平台）會用 PORT 環境變數指定對外埠號，
    # 並要求綁定 0.0.0.0 才能從容器外連進來；本機沒有 PORT 時退回 7860。
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
