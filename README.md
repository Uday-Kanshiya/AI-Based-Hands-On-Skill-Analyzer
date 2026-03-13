# AI Skill Analyzer

This repository contains the full-stack system for the **AI Hands-On Persona Analyzer**. It is designed to automatically collect, process, and analyze a user's technical footprint (e.g., GitHub history, resume, URLs, demo videos) to generate a "Hands-On Persona Profile."

## System Architecture

The application is split into two main components:
1. **Backend API (FastAPI + Python)**
   - Extracts data from GitHub, parses Resumes (PDF), and transcribes Demo Videos using `yt-dlp` and `whisper`.
   - Runs a scoring algorithm (`scorer.py`) over the extracted signals.
   - Serves the aggregated JSON data securely via REST endpoints (`api.py`).
2. **Frontend UI (Vanilla HTML/CSS/JS + Chart.js)**
   - A single-page, glassmorphic design that allows students to input their information.
   - Fetches profile data from the REST API.
   - Renders animated score breakdowns, GitHub language doughnuts, and technical insights.

## Scoring Methodology

The scoring framework evaluates practical engineering ability out of 100 points, broken into 4 categories:
1. **Project Evidence Score (30 pts)**: Weighted by the number of original (non-forked) repositories, total combined stars, and the presence of validated, live deployment URLs.
2. **GitHub Activity Score (30 pts)**: Weighed by followers, the number of distinct programming languages used across public repositories, and the sheer volume of public repositories.
3. **Engineering Practice Score (20 pts)**: Based on the density of technical skills/languages identified in the attached resume and demo videos.
4. **Collaboration Score (20 pts)**: Evaluates collaborative efforts (proxied through the ratio of forked repositories/open source involvement vs total repositories).

**Personas Identified**:
- **Builder**: Score >= 80
- **Explorer**: Score >= 60 and High Project Evidence
- **Academic**: Score >= 40 and High Activity/Research but low links
- **Beginner**: Score < 40 or empty profiles

## Setup & Deployment

**Prerequisites:**
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (required for transcribing audio)
- GitHub Personal Access Token (`.env` file) to prevent strict API rate limiting.

### 1. Backend Server
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi uvicorn pydantic python-multipart httpx
```

*Create a `.env` file from the `.env.template` and add your `GITHUB_TOKEN`.*

Run the REST API:
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Interface
Since the frontend uses zero-build, plain HTML/CSS/JS with CDN links, you just need to serve the root directory containing `index.html`. 
```bash
# In a new terminal, serve the frontend:
python -m http.server 8080
```
Navigate to `http://localhost:8080` in your browser.

## Sample Profiles to Test

To test the application, launch the UI and try entering these GitHub profiles:
1. `torvalds` (High activity, Explorer/Builder tier)
2. `defunkt` (GitHub co-founder)
3. Your own GitHub username! 
