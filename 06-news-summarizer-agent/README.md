# News Summarizer Agent

Fetches news articles on any topic and produces a polished briefing with a Flask-based UI.

**Frontend**: Flask + HTML + CSS  
**LLM**: Ollama with the model gpt-oss:120b-cloud  
**Data**: NewsAPI (optional — runs with sample data without a key)

## Setup

```bash
pip install -r requirements.txt
```

Make sure Ollama is running locally and that the configured model is available:

```bash
ollama pull gpt-oss:120b-cloud
```

## Run

```bash
python agent.py
```

Then open http://127.0.0.1:5000 in your browser.

Works without a NewsAPI key using sample data. For real news, add a NEWS_API_KEY to your environment.
