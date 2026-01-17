# Sử dụng Python base image nhẹ
FROM python:3.9-slim

# Cài đặt thư viện hệ thống cần thiết cho thư viện ảnh (OpenCV/Pillow)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file thư viện và cài đặt
COPY requirements.txt .
# Cài đặt với flag --no-cache-dir để giảm dung lượng image
# Cài torch CPU version cho nhẹ (trừ khi bạn setup GPU Docker)
RUN pip install --no-cache-dir -q -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy toàn bộ code vào
COPY . .

# Mở port 8000
EXPOSE 8000

# Lệnh chạy app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]