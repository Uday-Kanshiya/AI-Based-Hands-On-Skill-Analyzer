import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SkillScorer:
    def __init__(self):
        pass
        
    def calculate_score(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a Hands-On Persona score based on the extracted data.
        Returns a dictionary containing the score, breakdown, persona, and insights.
        """
        logging.info("Calculating Hands-On Persona Score...")
        
        # Initialize default metrics
        github_data = pipeline_data.get("github_data", {}) or {}
        resume_data = pipeline_data.get("resume_data", {}) or {}
        link_validation = pipeline_data.get("link_validation", {}) or {}
        
        # 1. Project Evidence Score (out of 30)
        # Based on number of repos, stars, and validated links
        repos = github_data.get("repos", []) if isinstance(github_data, dict) else []
        public_repos_count = int(github_data.get("public_repos_count", 0)) if isinstance(github_data, dict) else 0
        
        # Count non-forked repos and total stars
        original_repos = 0
        total_stars = 0
        for repo in repos:
            if isinstance(repo, dict) and not repo.get("is_fork", True):
                original_repos += 1  # type: ignore
                total_stars += int(str(repo.get("stars", 0)))  # type: ignore
        
        # Validated links bonus
        active_links = 0
        if isinstance(link_validation, dict):
            active_links = sum(1 for link_data in link_validation.values() if isinstance(link_data, dict) and link_data.get("status_code") == 200)
        
        project_score = min(30, (int(original_repos) * 2) + (int(total_stars) * 1) + (int(active_links) * 5))
        
        # 2. GitHub Activity Score (out of 30)
        # Based on followers and diverse languages
        followers = int(github_data.get("followers", 0)) if isinstance(github_data, dict) else 0
        top_languages = github_data.get("top_languages", {}) if isinstance(github_data, dict) else {}
        unique_languages = len(top_languages) if isinstance(top_languages, dict) else 0
        
        activity_score = min(30, (int(followers) * 1) + (int(unique_languages) * 3) + (int(public_repos_count) * 1))

        # 3. Engineering Practice Score (out of 20)
        # Based on resume skills matching technical buzzwords and video transcripts
        skills_found = resume_data.get("skills_found", []) if isinstance(resume_data, dict) else []
        engineering_score = min(20, len(skills_found) * 2) if isinstance(skills_found, list) else 0
        
        # If they took the effort to submit a video, give them points
        video_transcripts = pipeline_data.get("video_transcripts", [])
        if video_transcripts and isinstance(video_transcripts, list) and len(video_transcripts) > 0:
            engineering_score = min(20, engineering_score + 10)
            
        # 4. Collaboration Score (out of 20)
        # We roughly proxy this by the number of repos vs original repos (forks imply collaboration)
        forked_repos = int(public_repos_count) - int(original_repos)
        collaboration_score = min(20, forked_repos * 2)
        
        # Overall Score
        total_score = project_score + activity_score + engineering_score + collaboration_score
        
        # Persona Logic
        persona = "Beginner"
        if total_score >= 80:
            persona = "Builder"
        elif total_score >= 60 and project_score > 15:
            persona = "Explorer"
        elif total_score >= 40 and activity_score > 15:
            persona = "Academic"
            
        # Insights
        insights = []
        if int(original_repos) > 5:
            insights.append("Shows strong initiative with multiple original projects.")
        if int(unique_languages) > 3:
            insights.append("Demonstrates versatility across multiple programming languages.")
        if int(active_links) > 0:
            insights.append("Has successfully deployed and hosted web applications.")
        if not insights:
            insights.append("Profile is still developing; recommend building and deploying more original projects.")
            
        return {
            "hands_on_score": int(total_score),
            "breakdown": {
                "project_evidence": int(project_score),
                "github_activity": int(activity_score),
                "engineering_practice": int(engineering_score),
                "collaboration": int(collaboration_score)
            },
            "persona": persona,
            "insights": insights,
            "metrics": {
                "original_repos": int(original_repos),
                "total_stars": int(total_stars),
                "unique_languages": int(unique_languages),
                "active_links": int(active_links),
                "resume_skills": len(skills_found)
            }
        }

if __name__ == "__main__":
    import json
    # Simple test
    scorer = SkillScorer()
    dummy_data = {
        "github_data": {
            "public_repos_count": 10,
            "followers": 5,
            "top_languages": {"Python": 5, "JavaScript": 3},
            "repos": [
                {"name": "repo1", "is_fork": False, "stars": 2},
                {"name": "repo2", "is_fork": True, "stars": 0}
            ]
        },
        "resume_data": {"skills_found": ["python", "react", "git"]},
        "link_validation": {"https://myapp.com": {"status_code": 200}},
        "video_transcripts": [{"transcript": "Hello"}]
    }
    print(json.dumps(scorer.calculate_score(dummy_data), indent=2))
