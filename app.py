import google.generativeai as genai
from flask import Flask, render_template, jsonify
import os
from typing_extensions import TypedDict
import json

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

instruction = """
You are a journalist for a tech article which posts about the latest tech news.
The article caters to engineers, and others alike with a similar context.
"""

class Article(TypedDict):
    title: str
    summary: str
    source: str

def fetch_tech_news():
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
    
    gen_cfg = genai.GenerationConfig(
        response_mime_type="application/json", response_schema=list[Article]
    )

    try:
        response = model.generate_content(
            "List 10 articles which outline the tech-related events of the last month.",
            generation_config=gen_cfg,
        )

        news = json.loads(response.text)
    except:
        news = []

    return news

@app.route("/")
def index():
    news = fetch_tech_news()
    return render_template("index.html", news_article=news)

if __name__=="__main__":
    app.run(debug=True, port=5001)
