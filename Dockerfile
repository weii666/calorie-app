# 食物熱量估算 App —— Cloud Run 部署用容器
FROM python:3.11-slim

WORKDIR /app

# 先只複製依賴清單，讓這層能被 Docker 快取（改 code 不必重裝套件）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再複製其餘程式碼
COPY . .

# Cloud Run 會覆寫這個變數；本機測試時給個預設值
ENV PORT=7860

# app.py 已讀取 PORT 並綁定 0.0.0.0
CMD ["python", "app.py"]
