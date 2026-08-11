"""News Summarizer Agent with a Flask UI and Ollama-backed summarization."""

import os
from typing import Any

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


def fetch_news(topic: str, count: int = 5) -> list[dict[str, Any]]:
    if not NEWS_API_KEY:
        return [
            {
                "title": f"Major development in {topic}",
                "description": f"Researchers announce a breakthrough in the {topic} space.",
                "url": "https://example.com/1",
                "source": {"name": "Tech News"},
            },
            {
                "title": f"{topic.title()} industry sees rapid growth",
                "description": f"New data shows strong momentum around {topic} adoption.",
                "url": "https://example.com/2",
                "source": {"name": "Business Daily"},
            },
            {
                "title": f"Experts weigh in on {topic} challenges",
                "description": f"Industry leaders discuss the practical barriers facing {topic}.",
                "url": "https://example.com/3",
                "source": {"name": "Science Weekly"},
            },
        ]

    url = (
        f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize={count}"
        f"&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("articles", [])


def summarize_news(topic: str, articles: list[dict[str, Any]]) -> str:
    articles_text = "\n\n".join(
        f"Title: {article.get('title', 'Untitled')}\n"
        f"Source: {article.get('source', {}).get('name', 'Unknown')}\n"
        f"Summary: {article.get('description', 'N/A')}"
        for article in articles[:5]
    )

    prompt = (
        "You are a senior news analyst. Create a concise briefing with: "
        "1) Top Story, 2) Key Themes (3 bullet points), 3) What to Watch, and 4) Quick Headlines.\n\n"
        f"Topic: {topic}\n\nArticles:\n{articles_text}"
    )

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
            "system": "You write polished, structured news briefings.",
        }
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Ollama returned an empty response.")
    except requests.RequestException as exc:
        return (
            f"Ollama summarization is currently unavailable. "
            f"Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is available. "
            f"Details: {exc}"
        )


@app.route("/", methods=["GET", "POST"])
def index():
    topic = "artificial intelligence"
    count = 5
    articles: list[dict[str, Any]] = []
    summary = ""
    error = ""

    if request.method == "POST":
        topic = (request.form.get("topic") or "artificial intelligence").strip() or "artificial intelligence"
        count = max(1, min(10, int(request.form.get("count") or 5)))

        try:
            articles = fetch_news(topic, count)
            summary = summarize_news(topic, articles)
        except Exception as exc:  # pragma: no cover - UI safety net
            error = f"Unable to generate briefing: {exc}"

    return render_template(
        "index.html",
        topic=topic,
        count=count,
        articles=articles,
        summary=summary,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
