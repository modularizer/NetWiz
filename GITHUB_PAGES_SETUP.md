# GitHub Pages Deployment Setup

## 🚀 Frontend Deployment to GitHub Pages

This project uses GitHub Pages to host the frontend as a static site, while the backend runs as a Docker container.

### 📋 Setup Steps

1. **Enable GitHub Pages**:
   - Go to your repository Settings → Pages
   - Source: "GitHub Actions"
   - Save

2. **Configure Repository Name**:
   - If your repo is `modularizer/netwiz`, your site will be at:
   - `https://modularizer.github.io/netwiz/`

3. **Update Frontend API URL**:
   - The frontend needs to know where your backend API is hosted
   - Update `frontend/src/services/api.ts` or similar to point to your backend

### 🔧 Frontend Configuration

The frontend build process:
- Uses `npm run build` to create static files
- Outputs to `frontend/dist/` directory
- Deploys to GitHub Pages automatically

### 🌐 Production URLs

- **Frontend**: `https://modularizer.github.io/netwiz/`
- **Backend API**: `http://localhost:5000`

### 📁 File Structure

```
frontend/
├── dist/                 # Built static files (deployed to GitHub Pages)
├── src/
│   ├── services/
│   │   └── api.ts       # Update this to point to your backend
│   └── ...
└── package.json
```

### 🔄 Workflow

1. **Push to main** → Frontend builds and deploys to GitHub Pages
2. **Backend** → Builds and pushes Docker image to GitHub Container Registry
3. **Production** → Deploy backend container, frontend served from GitHub Pages

### 🛠️ Local Development

```bash
# Frontend (served locally)
cd frontend
npm run dev

# Backend (Docker)
docker-compose up --build backend mongodb
```

### 🌍 Production Deployment

```bash
# Deploy backend only (frontend is on GitHub Pages)
docker-compose -f docker-compose.prod.yml up
```
