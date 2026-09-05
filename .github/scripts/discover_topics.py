import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types

# 1. Fetch Trending Papers from Hugging Face API
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

# 2. Evaluate with Gemini 2.5 Flash
def evaluate_topics(papers):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an expert technical editor and AI system architect for paulwelch.dev.
    Review these raw AI releases from the past week and recommend 3 to 5 candidate topics for upcoming blog posts.

    Target Audience: Senior engineers, technical leaders, and AI enthusiasts.
    Tone: Deep technical understanding communicated clearly without fluff.

    Raw Inputs:
    {json.dumps(papers, indent=2)}

    Return a JSON list of candidates matching this schema:
    [
      {{
        "title": "Punchy, accessible proposed post title",
        "core_concept": "1-2 sentence summary of the breakthrough",
        "why_it_matters": "Why an engineering leader or builder should care",
        "technical_hook": "Specific architecture, paper, or repo link",
        "target_angle": "How we will make it intuitive/accessible",
        "difficulty_score": 1 to 5
      }}
    ]
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TopicList,
        )
    )
    return json.loads(response.text)

if __name__ == "__main__":
    papers = get_huggingface_papers()
    if papers:
        candidates = evaluate_topics(papers)
        # Write output to a file for GitHub Actions to read
        with open("candidates.json", "w") as f:
            json.dump(candidates, f, indent=2)
