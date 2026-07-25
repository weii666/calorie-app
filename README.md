---
title: 食物熱量估算
emoji: 🍱
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
---

# 🍱 食物熱量估算 App

上傳一張照片，透過 Google Gemini 視覺模型估算食物的大概熱量；
若照片不是食物，會回覆「這個不是食物」。

## 功能

- 📷 上傳食物照片 → 顯示食物名稱與估算熱量（kcal）
- 🚫 非食物照片 → 回覆「這個不是食物」
- 🤖 使用 Google Gemini（`gemini-flash-latest`）視覺模型

> 模型使用 `gemini-flash-latest` 別名（而非固定的 `gemini-2.5-flash`），
> 會自動跟隨 Google 當前的穩定 flash 模型，避免因特定版本下架而失效。

## 專案結構

| 檔案 | 用途 |
|------|------|
| `app.py` | 主程式（Gradio 介面 + Gemini 視覺辨識） |
| `README.md` | 說明文件，含 HF Space 設定的 YAML metadata |
| `requirements.txt` | HF Space 安裝依賴用（釘住實測版本） |
| `pyproject.toml` / `uv.lock` | uv 本機環境與鎖定版本 |
| `.env.example` | API key 範本（實際的 `.env` 不進版控） |

## 本機執行

本專案使用 [uv](https://docs.astral.sh/uv/) 管理虛擬環境，不會弄髒系統 Python。

```bash
# 1. 安裝依賴（會自動建立 .venv）
uv sync

# 2. 設定 Google API key
cp .env.example .env
# 編輯 .env，填入你的 GOOGLE_API_KEY

# 3. 執行
uv run app.py
```

啟動後開啟終端機顯示的網址（預設 http://127.0.0.1:7860）。

## 部署到 Hugging Face Space

1. 在 https://huggingface.co/new-space 建立一個 **Gradio** Space。
2. 在 Space 的 **Settings -> Variables and secrets** 新增一個 Secret：
   - Name：`GOOGLE_API_KEY`
   - Value：你的 Google API key
3. 把本 repo push 到該 Space 的 git remote（需要 HF 的 write token）：

```bash
git remote add space https://huggingface.co/spaces/<你的帳號>/<space 名稱>
git push space main
```

> 不要把 `GOOGLE_API_KEY` commit 進 repo，一律用 Space 的 Secret 設定。

## 取得 API key

- Google API key：https://aistudio.google.com/apikey
- Hugging Face token（部署用，需 Write 權限）：https://huggingface.co/settings/tokens
