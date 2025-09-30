# EasyLaw Setup Guide

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** 
- **Docker & Docker Compose**
- **Git**

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/ndtp2003/EasyLaw.git
cd EasyLaw
```

2. **Backend Environment Setup**
```bash
cd backend
# Copy environment template
cp config/.env.dev.template config/.env.dev
cp config/.env.prod.template config/.env.prod

# Edit .env.dev with your credentials:
# - GEMINI_API_KEY=your-gemini-api-key
# - MONGODB_URI=your-mongodb-atlas-uri
# - MILVUS_URI=your-milvus-cloud-uri
# - JWT_SECRET=your-secret-key
# - ADMIN_EMAIL=your-admin-email
```

3. **Frontend Environment Setup**
```bash
cd frontend
npm install
```

## 🛠️ Development Mode

### Option 1: Local Development
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
uvicorn app.main:app --reload --env-file config/.env.dev

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Option 2: Docker Development
```bash
# Start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f backend
```

## 🌍 Production Deployment

### Render/Heroku Backend
1. Create new app on Render/Heroku
2. Connect GitHub repository
3. Set environment variables from `.env.prod.template`
4. Deploy from `backend/` directory

### Vercel/Netlify Frontend
1. Create new project on Vercel/Netlify
2. Connect GitHub repository
3. Set build directory to `frontend/`
4. Set build command: `npm run build`
5. Set publish directory: `dist/`

## 🔧 Required Services

### MongoDB Atlas (Free Tier)
1. Create account at [MongoDB Atlas](https://cloud.mongodb.com)
2. Create free cluster
3. Get connection string
4. Add to `MONGODB_URI` in environment

### Zilliz Cloud (Milvus) (Free Tier)
1. Create account at [Zilliz Cloud](https://cloud.zilliz.com)
2. Create free cluster
3. Get connection details
4. Add to `MILVUS_URI`, `MILVUS_USER`, `MILVUS_PASSWORD`

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Add to `GEMINI_API_KEY`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test
```

## 📁 Project Structure

```
EasyLaw/
├── backend/                 # FastAPI Backend
│   ├── app/                # Application code
│   │   ├── controllers/    # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access
│   │   ├── models/         # Database models
│   │   ├── schemas/        # API schemas
│   │   ├── core/           # Core configs
│   │   └── utils/          # Utilities
│   ├── config/             # Environment configs
│   ├── requirements/       # Python dependencies
│   └── tests/              # Backend tests
├── frontend/               # React Frontend
│   ├── src/                # Source code
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── hooks/          # React hooks
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utilities
│   └── public/             # Static assets
├── docker/                 # Docker configurations
└── docs/                   # Documentation
```

## ⚡ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Chat
- `GET /api/v1/chat/sessions` - Get user sessions
- `POST /api/v1/chat/sessions` - Create new session
- `POST /api/v1/chat/message` - Send message
- `WS /ws/chat/{session_id}` - WebSocket chat

### Admin
- `POST /api/v1/admin/crawl-laws` - Crawl laws
- `POST /api/v1/admin/upload-laws` - Upload internal laws
- `POST /api/v1/admin/agent-chat` - Admin agent commands
- `GET /api/v1/admin/stats` - System statistics

## 🔒 Security Notes

- Never commit `.env` files to repository
- Use strong JWT secrets in production
- Enable HTTPS in production
- Configure proper CORS origins
- Use environment-specific MongoDB databases

## 📞 Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Contact: [Your Contact Info]
