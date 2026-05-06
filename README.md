# 🟣 HexaLearn — AI-Powered Japanese Learning Platform

A full-stack Japanese language learning platform built with Django REST Framework, integrating Google Gemini AI, Spaced Repetition System, and Japanese NLP.

**Live demo:** [hexalearn.ddns.net](http://hexalearn.ddns.net)

---

## Features

- **Flashcard (SRS)** — Spaced Repetition System based on SM-2 algorithm. Dynamic interval per user per card
- **AI Deck Generator** — Generate a full flashcard deck from a single seed word using Google Gemini (semantic field expansion)
- **AI Reading Assistant** — Real-time grammar explanation, paragraph summary, and vocabulary analysis via streaming (SSE)
- **Japanese Dictionary** — Word & Kanji lookup with furigana, meanings per language, pronunciations, and example sentences
- **Vocabulary Auto-detect** — Automatic vocabulary tagging per paragraph using Fugashi (MeCab Japanese NLP tokenizer)
- **JWT Authentication** — Access/refresh token with blacklist support and soft-delete account
- **Cloudinary Direct Upload** — Pre-signed credential flow, client uploads directly without passing through server

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6, Django REST Framework |
| Database | PostgreSQL (AWS RDS) |
| AI | Google Gemini 2.5 Flash Lite |
| NLP | Fugashi (MeCab binding for Japanese) |
| Media | Cloudinary |
| Auth | SimpleJWT |
| API Docs | drf-spectacular (Swagger / ReDoc) |
| Web Server | Gunicorn |
| Proxy | Nginx Alpine |
| Container | Docker, Docker Compose |
| Cloud | AWS EC2 (t2.micro), AWS RDS |

---

## Project Structure

```
hexalearn/
├── apps/
│   ├── home/          # Config, Language, Level, UserProfile
│   ├── account/       # JWT Auth, upload credentials
│   ├── dict/          # Dictionary: Word, Kanji, SavedWordList
│   ├── deck/          # Flashcard, SRS, AI Generator
│   └── reading/       # Passage, Paragraph, AI Reading Assistant
├── hexalearn/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── entrypoint.prod.sh
└── requirements.txt
```

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/hexalearn.git
cd hexalearn
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/hexalearn
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Run migrations & start server

```bash
python manage.py migrate
python manage.py runserver
```

API docs available at: `http://localhost:8000/`

---

## Docker (Production)

```bash
docker compose up --build -d
```

Services:
- `hexalearn_aws` — Django + Gunicorn (port 8000 internal)
- `hexalearn_aws_nginx` — Nginx reverse proxy (port 80 public)

> **Note:** This repo uses the lightweight AWS version with **Python threading** instead of Celery + Redis to fit within AWS Free Tier (t2.micro, 1GB RAM), saving ~200MB RAM.

---

## AI Integration

### Deck Generator
Generates a complete flashcard deck from a single seed word.
Gemini finds semantically related words, adds furigana, meanings, and hints.

```
POST /api/deck/v1/decks/{id}/generate/
Body: { "seed_word_id": 1, "target_count": 20 }
```

### Reading Assistant (Streaming)
Explains grammar, summarizes paragraphs, and lists vocabulary in real-time.

```
POST /api/reading/v1/passages/{id}/paragraphs/{id}/explain/
Body: { "selected_text": "食べる" }
```

---

## API Documentation

| URL | Description |
|---|---|
| `/` | Swagger UI |
| `/redoc/` | ReDoc |
| `/schema/` | OpenAPI schema (JSON) |

---

## 📄 License

MIT License — feel free to use and modify.
