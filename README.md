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
| `Dockerfile` | Cloud Run 部署用容器定義 |
| `.dockerignore` | 排除不需打包進映像的檔案 |
| `requirements.txt` | 依賴清單（釘住實測版本） |
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

## 部署到 Google Cloud Run

程式會讀取 `PORT` 環境變數並綁定 `0.0.0.0`，符合 Cloud Run 需求。
API key 以 Secret Manager 管理，不寫死在映像裡。

### 首次部署

```bash
# 1. 設定專案並啟用所需 API
gcloud config set project <你的 PROJECT_ID>
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com

# 2. 把 API key 存進 Secret Manager
printf '%s' '<你的 GOOGLE_API_KEY>' | \
  gcloud secrets create GOOGLE_API_KEY --replication-policy=automatic --data-file=-

# 3. 授權 Cloud Run 執行時的 service account 讀取該 secret
PROJECT_NUM=$(gcloud projects describe <你的 PROJECT_ID> --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 4. Build + Deploy（Cloud Build 依 Dockerfile 建映像）
gcloud run deploy calorie-app \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest
```

### 之後更新程式碼

secret 與權限都設好後，只要重跑部署指令即可：

```bash
gcloud run deploy calorie-app --source . --region asia-east1
```

### 更換 API key

```bash
printf '%s' '<新的 key>' | gcloud secrets versions add GOOGLE_API_KEY --data-file=-
gcloud run deploy calorie-app --source . --region asia-east1  # 重新部署以抓 latest
```

> 不要把 `GOOGLE_API_KEY` commit 進 repo，一律用 Secret Manager 管理。

## 取得 API key

- Google API key：https://aistudio.google.com/apikey
