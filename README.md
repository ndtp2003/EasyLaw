# EasyLaw - AI-Powered Legal Assistant

## 🏗️ Architecture
- **Backend**: Python + FastAPI (Clean Architecture)
- **Frontend**: React + TypeScript + Tailwind + shadcn/ui
- **Database**: MongoDB Atlas + Milvus (Vector DB)
- **AI**: Google Gemini API (LLM + Embeddings)
- **Deployment**: Docker + Render/Heroku + Vercel

## 🚀 Features
- **User Features**: JWT Auth, 3 Active Sessions, Dual RAG Modes, WebSocket Chat
- **Admin Features**: Law Crawling, Document Upload, Function Calling, Analytics

## 📁 Project Structure
```
EasyLaw/
├── backend/                 # FastAPI Backend
│   ├── app/                # Main application
│   ├── config/             # Environment configs (dev/prod)
│   ├── tests/              # Unit & integration tests
│   └── requirements/       # Dependencies
├── frontend/               # React Frontend
│   ├── src/                # Source code
│   └── public/             # Static assets
├── docker/                 # Docker configurations
├── docs/                   # Documentation
└── scripts/                # Deployment scripts
```

## 🛠️ Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements/dev.txt
uvicorn app.main:app --reload --env-file .env.dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🌍 Environment Configuration
- `.env.dev` - Development environment
- `.env.prod` - Production environment
- Environment variables managed per deployment target

## 📋 TODO
- [x] Project structure setup
- [ ] Backend core implementation
- [ ] Frontend core implementation
- [ ] AI integration (Gemini + Milvus)
- [ ] Admin dashboard
- [ ] Deployment setup
