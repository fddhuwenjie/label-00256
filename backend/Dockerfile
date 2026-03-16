FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载 Swagger UI 静态资源到镜像内，不依赖外部 CDN
RUN pip install --no-cache-dir swagger-ui-bundle==1.1.0

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
