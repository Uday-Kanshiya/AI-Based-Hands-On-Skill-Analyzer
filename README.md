# AI Skill Analyzer

This repository contains the full-stack system for the **AI Hands-On Persona Analyzer**. It is designed to automatically collect, process, and analyze a user's technical footprint (e.g., GitHub history, resume, URLs, demo videos) to generate a "Hands-On Persona Profile."

## Method of Approach & System Architecture

The application is split into two main components operating seamlessly together:
1. **Data Collection Pipeline (FastAPI + Python)**
   - **GitHub Integration:** Uses a Personal Access Token to bypass strict API rate limits, extracting the user's public repositories, stars, followers, and language statistics using `PyGithub`.
   - **Resume Processing:** Uploaded PDF Resumes are parsed by `pdfplumber`, utilizing Natural Language Processing (regex/keyword extraction) to mine technical skills and certifications.
   - **Link Validation:** Custom scripts scrape and validate live deployment URLs provided by the user.
   - **Video Analysis:** Optionally uses `yt-dlp` to download demo video audio, transcribing it via OpenAI's `whisper` model to detect spoken technical jargon and soft skills.
2. **Analysis Engine & Frontend Interface (Vanilla HTML/CSS/JS)**
   - Runs a heuristic scoring algorithm (`scorer.py`) over the extracted signals to formulate an objective persona.
   - Serves an interactive, glassmorphic presentation layer containing radar charts and doughnut graphs powered by `Chart.js`.

## Data Collection & Extraction

The backend pipeline extracts four primary "Signals" to perform an objective evaluation:
- **Code & Repository Signals:** Pulls original, non-forked repositories. It identifies commit frequencies, languages utilized, and community engagement (Stars/Forks).
- **Practical Deployment Signals:** Validates user-provided URLs to verify the existence of deployed, working applications vs. theoretical code.
- **Documentation & Resume Signals:** Analyzes text from provided PDF resumes to verify skill density and technical communication ability.
- **Demonstration Signals:** Listens to provided spoken-word demo videos to measure the ability to articulate technical concepts securely.

## Evaluation Criteria & Scoring Methodology

The scoring framework evaluates practical engineering ability out of a maximum of 100 points, strictly allocated across 4 robust categories:

1. **Project Evidence Score (Maximum 30 pts):** 
   - Weighted heavily by the number of original (non-forked) repositories.
   - Factors in total combined stars across all original work.
   - Rewards the presence of validated, live deployment URLs demonstrating end-to-end delivery capability.

2. **GitHub Activity Score (Maximum 30 pts):**
   - Weighed by community followers and social proof.
   - Analyzes the breadth of the developer by counting distinct programming languages used natively in their repositories.

3. **Engineering Practice Score (Maximum 20 pts):**
   - Assesses the density of technical skills/languages explicitly identified in the attached Resume and transcribed demo videos.

4. **Collaboration Score (Maximum 20 pts):**
   - Evaluates teamwork and open-source engagement. Proxied through the ratio of forked repositories and involvement in external codebases vs. isolated solo repositories.

**Personas Identified**:
Based on the final score calculation, candidates are assigned a Persona:
- 🏆 **Builder**: Score >= 80 (Demonstrates high volume of original work and completed deployments).
- 🧭 **Explorer**: Score >= 60 (High project evidence and linguistic breadth).
- 📚 **Academic**: Score >= 40 (High activity/research focus but low practical links).
- 🌱 **Beginner**: Score < 40 (Or largely empty digital profiles).

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

## Resume Evaluation Case Study

The system goes beyond just counting repositories. Here is an example of how a standard software engineering resume is evaluated by the pipeline:

### Input Scenario
- **Given:** A 1-page PDF Resume for a Full-Stack Developer applicant.
- **Content:** The resume details academic history and lists skills like "Python", "React", "Docker", "AWS", and "SQL" scattered in paragraphs.
- **Deployment Links:** Provided 1 live portfolio link (`https://my-portfolio.dev`).

### System Output & Persona Classification
1. **Data Collection:** The `pdfplumber` pipeline scans the document and identifies 5 distinct hard-skills matching our heuristic database. The `link_validator.py` confirms the portfolio link returns an HTTP 200 Status Code.
2. **Calculations:** 
   - The user is awarded baseline *Engineering Practice* points for the 5 localized skills.
   - They receive bonus *Project Evidence* points for the verified live deployment.
3. **Assessment:** Assuming an average GitHub history alongside this resume, the applicant crosses the 60+ threshold and is proudly classified as an **Explorer Persona**, meaning they provide tangible evidence of their capabilities beyond just academic text.
