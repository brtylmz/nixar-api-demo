FROM python:3.9-slim

# Gerekli sistem kütüphanelerini yüklüyoruz (Nixar Core için zorunlu)
# Nixar Linux version libzmq3, libsodium ve pgsql cüzdanları için libpq gerektirir
RUN apt-get update && apt-get install -y \
    build-essential \
    libzmq3-dev \
    libsodium-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Python bağımlılıklarını kurma
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyalama
COPY . /app/

# Linux için libnixar_core.so'nun yolu ortam değişkenine ekleniyor
# Kullanıcı x86_64 veya aarch64 mimarisine göre uygun olanı seçebilir, biz şimdilik ubuntu_20 yolunu kullanıyoruz
ENV LD_LIBRARY_PATH=/app/nixar_api_linux/ubuntu_20:/app/nixar_api_linux/x86_64-unknown-linux-gnu:$LD_LIBRARY_PATH

# FastAPI Portu
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
