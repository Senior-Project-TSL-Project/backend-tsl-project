# Thai Sign Language API 🤟

API สำหรับแปลงข้อความภาษาไทยเป็น Sign Language Gloss โดยใช้โมเดล MT5

## 📁 โครงสร้างโปรเจค

```
backend-tsl-project/
├── app/
│   ├── __init__.py       # Package init
│   ├── config.py         # ตั้งค่า (model path, device)
│   ├── schemas.py        # Pydantic models
│   ├── model_service.py  # โหลดและ predict โมเดล
│   └── routes.py         # API endpoints
├── model/                # โฟลเดอร์โมเดล MT5
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker image
├── docker-compose.yml   # Docker Compose
└── README.md
```

---

## 🚀 วิธีรันบน MacBook

### วิธีที่ 1: รันแบบ Local (แนะนำสำหรับ Development)

```bash
# 1. สร้าง Virtual Environment
python3 -m venv venv

# 2. เปิดใช้งาน Virtual Environment
source venv/bin/activate

# 3. ติดตั้ง Dependencies
pip install -r requirements.txt

# 4. รัน Server
python main.py
# หรือ
uvicorn main:app --reload
```

Server จะรันที่ `http://localhost:8000`

---

### วิธีที่ 2: รันด้วย Docker 🐳

#### ติดตั้ง Docker Desktop (ครั้งแรก)

1. ดาวน์โหลด Docker Desktop จาก https://www.docker.com/products/docker-desktop
2. ติดตั้งและเปิด Docker Desktop
3. รอจนกว่า Docker จะพร้อมใช้งาน (ไอคอนเป็นสีเขียว)

#### รันด้วย Docker Compose (แนะนำ)

```bash
# Build และ Run
docker compose up --build

# รันแบบ Background
docker compose up -d --build

# ดู Logs
docker compose logs -f

# หยุดการทำงาน
docker compose down
```

#### รันด้วย Docker โดยตรง

```bash
# 1. Build Image
docker build -t tsl-api .

# 2. Run Container
docker run -p 8000:8000 tsl-api
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | ข้อมูล API |
| `/health` | GET | ตรวจสอบสถานะ |
| `/predict` | POST | แปลงข้อความเป็น gloss |
| `/docs` | GET | Swagger UI |

### ตัวอย่างการใช้งาน

```bash
# ตรวจสอบสถานะ
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "สวัสดีครับ"}'
```

### ตัวอย่าง Response

```json
{
  "input_text": "สวัสดีครับ",
  "gloss": "สวัสดี",
  "confidence": 87.5
}
```

---

## 📖 API Documentation

เข้าดู Interactive API Docs ได้ที่:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
