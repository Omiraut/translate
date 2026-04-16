# QUICKSTART - Get Running in 2 Minutes

## Prerequisites
- Python 3.8+
- pip

## 🚀 3-Step Setup

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Start the API
```bash
python main.py
```

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3️⃣ Test It (Open Another Terminal)
```bash
# Simple test
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi", "language": "hi"}'
```

**Response:**
```json
{
  "status": true,
  "code": 200,
  "message": "Translation successful",
  "data": {
    "converted_text": "नमस्ते",
    "language": "hi",
    "cached": false
  }
}
```

---

## 📚 View Auto Documentation
```
http://localhost:8000/docs
```
Open in browser → Interactive Swagger UI

---

## 🎯 Run Full Demo
```bash
python demo.py
```

Runs:
- Health check
- Language listing
- 8 example translations
- Cache testing
- Error handling
- Statistics

---

## 🐳 Alternative: Docker

### Single Command (with Docker installed)
```bash
docker build -t translation-api . && \
docker run -p 8000:8000 translation-api
```

Or with docker-compose:
```bash
docker-compose up
```

---

## 📝 Example Requests

### Hindi
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "hi"}'
# Response: "नमस्ते"
```

### Marathi
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Good morning", "language": "mr"}'
# Response: "सुप्रभात"
```

### Gujarati
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Thank you", "language": "gu"}'
# Response: "તમારું આભાર"
```

---

## 📊 All Languages
```bash
curl http://localhost:8000/languages
```

Supports: Hindi, Marathi, Gujarati, Bengali, Tamil, Telugu, Kannada, Malayalam + 10 more

---

## 📈 Check Stats
```bash
curl http://localhost:8000/stats
```

View:
- Total translations
- Cache hits
- Cached entries

---

## ✅ Health Check
```bash
curl http://localhost:8000/health
```

Response: `{"status": "ok"}`

---

## 🧪 Run Tests
```bash
pip install pytest
pytest tests.py -v
```

---

## 🔧 Advanced Configuration

Edit `.env` to change:
```
PORT=8000              # Change server port
RATE_LIMIT_REQUESTS=60  # Change rate limit
CACHE_TTL_MINUTES=60    # Cache duration
```

Then restart the API.

---

## 📄 Full Documentation
See `README.md` and `API_DOCUMENTATION.md`

---

## 🆘 Troubleshooting

**"Connection refused"**
- Make sure API is running: `python main.py`

**"Rate limit exceeded"**
- Change `RATE_LIMIT_REQUESTS` in `.env`

**"Import error"**
- Reinstall: `pip install -r requirements.txt --force-reinstall`

---

## 🎉 That's It!

You now have a production-ready Translation API running locally.

Next: Explore the interactive docs at http://localhost:8000/docs

