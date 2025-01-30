from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")

instruction = """
You are a journalist for a tech article which posts about the latest tech news.
The article caters to engineers, and others alike with a similar context.
"""

def fetch_tech_news():
    # make API request for news in JSON

    news = []
    return news

@app.route("/")
def index():
    news = fetch_tech_news()
    return render_template("index.html", news_article=news)

if __name__=="__main__":
    app.run(debug=True, port=5001)
