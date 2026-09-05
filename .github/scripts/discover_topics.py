import os
import json
import urllib.request
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Pydantic Schemas
# ---------------------------------------------------------------------------
class TopicCandidate(BaseModel):
    title: str = Field(description="Punchy, accessible proposed post title")
    core_concept: str = Field(description="1-2 sentence summary of the breakthrough")
    why_it_matters: str = Field(description="Why an engineering leader or builder should care")
    technical_hook: str = Field(description="Specific architecture, paper, or repo link")
    target_angle: str = Field(description="How we will make it intuitive/accessible")
    difficulty_score: int = Field(description="Technical depth rating from 1 to 5")

class TopicList(BaseModel):
    candidates: list[TopicCandidate]

# ---------------------------------------------------------------------------
# 2. Ingestion
# ---------------------------------------------------------------------------
def get_huggingface_papers():
    url = "https://huggingface.co/api/daily_papers"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return [{
                'title': p['paper']['title'],
                'summary': p['paper']['summary'],
                'url': f"https://huggingface.co/papers/{p['paper']['id']}"
            } for p in data[:10]]
    except Exception as e:
        print(f"Error fetching HF papers: {e}")
        return []

# ---------------------------------------------------------------------------
# 3. Evaluation
# ---------------------------------------------------------------------------
def evaluate_topics(papers):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an expert technical editor and AI system architect for paulwelch.dev.
    Review these raw AI releases from the past week and recommend 4 to 9 candidate topics for upcoming blog posts.

    Target Audience: Senior engineers, technical leaders, and AI enthusiasts.
    Tone: Deep technical understanding communicated clearly without fluff.

    Raw Inputs:
    {json.dumps(papers, indent=2)}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",  # Active model ID
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TopicList,
        )
    )
    
    result = json.loads(response.text)
    return result.get("candidates", [])

# ---------------------------------------------------------------------------
# 4. Main Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    papers = get_huggingface_papers()
    if papers:
        candidates = evaluate_topics(papers)
        with open("candidates.json", "w") as f:
            json.dump(candidates, f, indent=2)
        print(f"Successfully generated {len(candidates)} candidate topics.")
    else:
        print("No papers fetched. Exiting.")
