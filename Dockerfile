# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# กำหนดโฟลเดอร์สำหรับเก็บ Cache ของ Hugging Face ให้เป็นสัดส่วน
ENV HF_HOME=/root/.cache/huggingface

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =================================================================
# จุดที่แก้ไข: ดาวน์โหลดโมเดลจาก Hugging Face มาเก็บไว้ใน Cache ตอน Build Image
# =================================================================
RUN python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
    model_name = 'HomieZ09/TSL-mt5'; \
    print(f'Downloading {model_name}...'); \
    AutoTokenizer.from_pretrained(model_name); \
    AutoModelForSeq2SeqLM.from_pretrained(model_name); \
    print('Model downloaded successfully!')"

# Copy application code
COPY app/ ./app/
COPY main.py .

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]