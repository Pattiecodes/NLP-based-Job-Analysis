# Job Skills NLP - AI-Powered Job Market Analysis

An intelligent web application that analyzes job postings using Natural Language Processing (NLP) to extract trending skills, identify job clusters, and provide insights into the job market. Built with React, Flask, and PostgreSQL.

## 🌟 Features

### Core Analytics
- **Dashboard Analytics**: Real-time statistics on job postings, skills, locations, and companies
- **Skill Extraction**: Automatically extract skills from job descriptions (120+ skills across all industries)
- **Job Categorization**: AI-powered classification into 20 diverse categories (Software, Healthcare, Education, Construction, Hospitality, and more)
- **Job Clustering**: K-Means clustering to group similar job postings
- **Topic Modeling**: LDA-based topic modeling to discover job market themes
- **Trending Skills**: Track the most in-demand skills with frequency analytics

### Data Management
- **Web Scraping**: One-click job scraping from Dashboard with category selector (12 predefined + custom)
- **File Upload**: Support for CSV, XLSX, and PDF job posting uploads
- **Data Export**: Download processed job data, trending skills, and analysis results as CSV
- **Auto-Categorization**: Every job automatically processed through NLP pipeline

### User Experience
- **Data Visualization**: Interactive charts using Recharts with 24-color palette
- **Responsive UI**: Clean interface with sidebar navigation
- **Optimized Performance**: Fast password hashing for quick sign-in

## 📁 Project Structure

```
ITS120L - Project/
├── backend/                  # Flask API server
│   ├── app.py               # Main Flask application
│   ├── models.py            # SQLAlchemy database models
│   ├── init_db.py           # Database initialization script
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment configuration
│   └── routes/
│       ├── dashboard_routes.py    # Dashboard API endpoints
│       ├── upload_routes.py       # File upload endpoints
│       └── analysis_routes.py     # ML model inference endpoints
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── components/      # Reusable components
│   │   │   └── Layout.jsx   # Sidebar navigation layout
│   │   └── pages/           # Page components
│   │       ├── Dashboard.jsx
│   │       ├── Upload.jsx
│   │       ├── Analysis.jsx
│   │       └── SearchPage.jsx
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── dataset/                 # Job posting datasets (Git LFS)
│   ├── job_skills.csv
│   ├── job_summary.csv
│   └── linkedin_job_postings.csv
├── output/                  # Trained ML models (Git LFS)
│   ├── tfidf_vectorizer.pkl
│   ├── kmeans_model.pkl
│   ├── lda_model.pkl
│   └── top_skills.csv
└── job_skills_nlp.ipynb     # Jupyter notebook with NLP analysis
```

## 🛠️ Tech Stack

### Backend
- **Flask 3.0** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy 3.1** - ORM
- **scikit-learn 1.3** - Machine learning
- **pandas 2.1** - Data processing
- **NLTK 3.8** - Natural language processing

### Frontend
- **React 18.2** - UI framework
- **Vite 5.0** - Build tool
- **React Router 6.20** - Routing
- **Recharts 2.10** - Data visualization
- **Axios 1.6** - HTTP client

## 🚀 Getting Started

### Localhost Quick Start (Windows, tested)

Use this exact flow for local testing.

1. **Open 2 terminals** at the project root.
2. **Backend terminal**
    ```bash
    cd backend
   py -3.12 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   set DISABLE_DAILY_SCRAPER=1
   python app.py
    ```
    Expected: Flask shows `Running on http://127.0.0.1:5000`
3. **Frontend terminal**
    ```bash
    cd frontend
   npm install
    npm.cmd run dev -- --host 127.0.0.1 --port 3000 --strictPort
    ```
    Expected: Vite shows `Local: http://127.0.0.1:3000/`
4. Open `http://127.0.0.1:3000` in your browser.

### If Port 3000 or 5000 Is Already In Use (Windows)

Run this once before starting servers:

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
   Where-Object { $_.LocalPort -in 3000,5000 } |
   Select-Object -Unique OwningProcess |
   ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Then start backend and frontend again.

### Backend Environment Notes

- For best compatibility across devices, use **Python 3.11 or 3.12** for backend setup.
- `DATABASE_URL` is optional for local smoke testing because the app falls back to local SQLite when unset.
- If needed, disable the background daily scraper in local testing:
   ```powershell
   $env:DISABLE_DAILY_SCRAPER='1'
   ```

### Prerequisites

- Python 3.11 or 3.12 recommended
- Node.js 18+
- PostgreSQL 14+
- Git LFS (for large dataset files)

PostgreSQL is optional for local testing. If `DATABASE_URL` is not set to PostgreSQL, the backend uses local SQLite.

### Localhost Quick Start (For Any Device)

1. Clone and pull large files:
   ```bash
   git clone <repo-url>
   cd "ITS120L - Project"
   git lfs install
   git lfs pull
   ```

2. Start backend:
   ```bash
   cd backend
   # Use Python 3.11 or 3.12
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   # Optional for local-only run:
   # set DISABLE_DAILY_SCRAPER=1  # Windows
   # export DISABLE_DAILY_SCRAPER=1  # macOS/Linux
   # Optional if you want DB seed on first run:
   # python init_db.py
   # python seed_data.py
   python app.py
   ```

3. Start frontend in another terminal:
   ```bash
   cd frontend
   npm install
   npm run dev -- --host 127.0.0.1 --port 3000 --strictPort
   ```

4. Open `http://127.0.0.1:3000`.

If dashboard data is empty on a fresh machine, run `python backend/seed_data.py` once.

## 🔧 Configuration

### Database Configuration

Create a PostgreSQL database:
```sql
CREATE DATABASE job_skills_nlp;
```

The application uses the following tables:
- `job_postings` - Job posting data
- `job_skills` - Skills extracted from jobs
- `trending_skills` - Aggregated skill trends
- `analysis_results` - ML model predictions
- `upload_history` - File upload tracking

### Environment Variables

Backend `.env` file:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/job_skills_nlp
FLASK_ENV=development
SECRET_KEY=your-secret-key
UPLOAD_FOLDER=uploads
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
REDIS_URL=redis://localhost:6379/0  # Optional for async tasks
MIN_SCRAPE_JOBS=50  # Minimum jobs saved per manual request and daily scrape
DAILY_SCRAPE_LIMIT=100  # Target jobs for midnight scheduler (must be >= MIN_SCRAPE_JOBS)
CRON_SECRET=your-random-long-secret  # Required to protect scheduled scrape endpoint
```

## 🚀 Free Deployment (No Vercel Required)

- Frontend: Render Static Site (build command: `npm install && npm run build`, publish directory: `dist`)
- Backend: Render Web Service (start command: `python app.py` from `backend/`)
- Database: Free PostgreSQL on Neon/Supabase (recommended for production)

### Midnight Scraper in Production

Use GitHub Actions scheduler so scraping runs even if free hosting sleeps.

Workflow file: `.github/workflows/midnight-scrape.yml`

Set these repository secrets in GitHub:
- `SCRAPE_API_URL` (example: `https://your-backend.onrender.com`)
- `CRON_SECRET` (must match backend `CRON_SECRET` env var)

Default schedule in workflow is daily at 12:00 AM UTC+8 (`0 16 * * *` in UTC).

### Render Deployment Steps (Recommended)

1. Deploy backend as **Render Web Service** from `backend/`.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
2. Set backend environment variables in Render:
   - `DATABASE_URL` (Neon/Supabase PostgreSQL URL)
   - `FLASK_ENV=production`
   - `SECRET_KEY=<your-secret>`
   - `FRONTEND_ORIGINS=https://<your-frontend-domain>`
   - `MIN_SCRAPE_JOBS=50`
   - `DAILY_SCRAPE_LIMIT=100`
   - `CRON_SECRET=<same-secret-used-in-github-actions>`
3. Deploy frontend as **Render Static Site** from `frontend/`.
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
   - Env var: `VITE_API_BASE_URL=https://<your-backend-domain>`
4. In GitHub repo secrets, set:
   - `SCRAPE_API_URL=https://<your-backend-domain>`
   - `CRON_SECRET=<same-secret-as-backend>`

This keeps your existing app features (NLP, upload, scraping, scheduled scraping) working in production.

### GitHub Pages Contingency (Optional) -- Still working on it

If Render's free tier has issues, you can deploy the frontend to GitHub Pages:

1. **Enable GitHub Pages** in repository settings (source: GitHub Actions)

2. **Set GitHub repository secret**:
   - `RENDER_API_URL` = your Render backend URL

3. **Deploy manually** from Actions tab:
   - Go to "Actions" → "Deploy to GitHub Pages" → "Run workflow"

The build automatically uses:
- Root path (`/`) for Render deployment (default)
- Subpath (`/NLP-based-Job-Analysis/`) for GitHub Pages
`

## 📊 API Endpoints

### Dashboard Routes
- `GET /api/dashboard/stats` - Get overall statistics (jobs, companies, locations, skills)
- `GET /api/dashboard/top-skills` - Get top trending skills (filtered, excluding meaningless words)
- `GET /api/dashboard/job-distribution` - Get job distribution by level, type, and category
- `GET /api/dashboard/top-companies` - Get top hiring companies
- `GET /api/dashboard/top-locations` - Get top hiring locations
- `GET /api/dashboard/topics` - Get LDA topic modeling results
- `GET /api/dashboard/clusters` - Get K-Means clustering results

### Scraping Routes
- `POST /api/scraping/jobs/trigger` - Trigger job scraping with NLP processing
  - Body: `{ "query": "nurse", "limit": 50, "source": "web_scraper" }`
- `GET /api/scraping/stats` - Get scraping statistics

### Upload Routes
- `POST /api/upload/file` - Upload job posting file (CSV/XLSX/PDF)
- `GET /api/upload/history` - Get upload history
- `GET /api/upload/status/<id>` - Get upload status

### Download Routes
- `GET /api/download/jobs` - Download all job postings as CSV
- `GET /api/download/skills` - Download trending skills as CSV (filtered)
- `GET /api/download/analysis` - Download all analysis results as CSV (requires seed data)
- `GET /api/download/clusters` - Download clustering results as CSV (requires seed data)
- `GET /api/download/topics` - Download topic modeling results as CSV (requires seed data)

**Note**: Only job postings and trending skills downloads are enabled by default. Advanced ML downloads (analysis, clusters, topics) require running `python backend/seed_data.py` first.

### Authentication Routes
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login (optimized password hashing)
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check authentication status
- `GET /api/auth/me` - Get current user profile

### Analysis Routes
- `POST /api/analysis/skills/extract` - Extract skills from text
- `POST /api/analysis/cluster/predict` - Predict job cluster
- `POST /api/analysis/topic/predict` - Predict topic distribution
- `GET /api/analysis/search` - Search job postings

## 🔬 Machine Learning Models

The application uses pre-trained models stored in the `output/` directory:

1. **TF-IDF Vectorizer** - Text feature extraction
2. **K-Means Clustering** - Job grouping (5 clusters)
3. **LDA Topic Model** - Topic discovery (5 topics)

Models were trained on LinkedIn job postings dataset with ultra-strict technical skill filtering.

## 📈 Data Processing Pipeline

1. **Data Collection**: Upload CSV/XLSX/PDF files OR trigger web scraping from Dashboard
2. **Automatic NLP Analysis**: Every scraped/uploaded job is processed through:
   - **Job Categorization**: Classifies jobs into 20 categories (Software, Healthcare, Education, Construction, etc.)
   - **Skill Extraction**: Extracts 120+ skills across all industries (tech, nursing, teaching, trades, etc.)
   - **Trending Skills**: Automatically tracks skill frequency across all jobs
   - **Cluster Prediction**: Assigns jobs to clusters (if ML model exists)
3. **Text Preprocessing**: Tokenization, lemmatization, stopword removal
4. **Feature Engineering**: TF-IDF vectorization
5. **Storage**: Save results to PostgreSQL
6. **Visualization**: Display insights on dashboard

### Seeding Analysis Data

To enable cluster and topic modeling downloads, populate sample analysis results:

```bash
cd backend
python seed_data.py
```

This creates:
- Sample clustering results (6 job clusters with keywords)
- Sample topic modeling results (5 LDA topics)
- Pre-populated trending skills

**Note**: The NLP analysis (categorization, skill extraction) runs automatically on every scrape. The seed script only populates the `AnalysisResult` table needed for advanced ML downloads.

## 🔄 Recent Updates & Future Enhancements

### ✅ Completed
- [x] Web scraping for automatic job data collection
- [x] Automated NLP processing pipeline (categorization + skill extraction)
- [x] Scheduled midnight scraping via GitHub Actions (5 diverse job types)
- [x] User authentication and authorization
- [x] Export reports as CSV (all data types)
- [x] 20 diverse job categories beyond tech (Healthcare, Education, Trades, etc.)
- [x] 120+ skills across all industries
- [x] GitHub Pages contingency deployment option
- [x] Optimized password hashing for faster sign-in

### 🔮 Future Enhancements
- [ ] Dynamic model retraining pipeline with new data
- [ ] Scheduled background tasks using Celery/Redis
- [ ] Email notifications for new job matches
- [ ] Saved searches and job alerts
- [ ] Export reports as PDF with charts
- [ ] Mobile responsive design improvements
- [ ] Job recommendation engine based on user preferences
- [ ] Salary range prediction using ML

## 📝 Git LFS

This project uses Git LFS for large files:
- `dataset/*.csv` (1.9GB total)
- `output/*.pkl` (ML models)
- `output/*.csv` (processed data)

Install Git LFS:
```bash
git lfs install
git lfs pull
```

## 👥 Contributors

- **James Patrick De Ocampo**

## 📄 License

This project is for educational purposes only.

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify database exists: `psql -l`

### Frontend Not Connecting to Backend
- Ensure backend is running on port 5000
- Check Vite proxy configuration in `vite.config.js`
- Verify CORS settings in Flask app

### Model Loading Error
- Verify models exist in `output/` directory
- Pull Git LFS files: `git lfs pull`

### Upload Fails
- Check file size limit (500MB max)
- Verify UPLOAD_FOLDER exists
- Check file format (CSV, XLSX, PDF only)

### Slow Sign-In Performance
The application uses optimized password hashing (pbkdf2:sha256 with 100k iterations) which provides security while maintaining fast response times. If sign-in is still slow, check:
- Database connection latency
- Server resources (CPU/memory)
- Network latency between frontend and backend

### Download Issues (Clusters/Topics)
If cluster or topic downloads show "No data available":
1. Run `python backend/seed_data.py` to populate sample analysis results
2. Or run your own ML analysis pipeline
3. Remember: basic job data and skills downloads work immediately after scraping

### Deployment Issues with SQLite Database
**Important:** The `.db` file is excluded from git (`backend/*.db` in `.gitignore`):
- **Local Development**: SQLite database works fine locally in `backend/instance/` (not tracked by git)
- **Production (Render/Cloud)**: Uses PostgreSQL via `DATABASE_URL` environment variable
- **Why**: Storing large SQLite files in git causes LFS quota issues. Cloud deployments use proper databases (PostgreSQL/Neon) instead.

This is intentional and correct — the application automatically uses PostgreSQL in production.

## 📞 Support

For issues and questions, please open an issue on GitHub or contact me via deocampojamespatrickcode@gmail.com


