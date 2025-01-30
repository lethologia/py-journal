from flask import Flask, render_template
from flask_caching import Cache
import requests
import os
import json

cache = Cache(config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
})
app = Flask(__name__)
cache.init_app(app)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

if not GEMINI_KEY or not UNSPLASH_KEY:
    raise OSError(f"Missing API Key. Gemini: {GEMINI_KEY}, Unsplash: {UNSPLASH_KEY}")

# unsplash api params
unsplash_api_endpoint = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_KEY}"

# configure gemini model
model = "gemini-1.5-flash-8b"
gemini_api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"

# gemini request parameters
headers = {
    "Content-Type": "application/json"
}

system_instruction = {
    "parts": { 
        "text": """You are a journalist for a tech article. 
        The article caters to people with a technical background like engineers. 
        When prompted with a topic, and number of articles, respond with the following JSON schema:
        
        [
        {
            "title": string,
            "summary": string,
            "date": string,
            "image_url": string,
        }
        ]        
        
        where:
        - image_url is a thumbnail image for the article.
        """
    }
}

contents = {
    "parts": {
        "text": "Show me 6 articles about tech news from the last month."
    }
}

tools = [{
    "google_search_retrieval": {
        "dynamic_retrieval_config": {
            "mode": "MODE_DYNAMIC",
            "dynamic_threshold": 0.4
        }
    }
}]

"""
gen_cfg = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "description": "A news article for the specified topic.",
            "properties": {
                "title": { "type": "STRING" },
                "summary": { "type": "STRING" },
                "image_url": { "type": "STRING" },
                "date": { "type": "STRING" }
            }
        }
    }
}
"""

params = {
    "system_instruction": system_instruction,
    "contents": contents,
    "tools": tools,
    #"generationConfig": gen_cfg
}

def test():
    response = requests.post(gemini_api_endpoint, headers=headers, json=params)
    #print(response.text)
    print(response.status_code)

    json_txt = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    json_txt = json_txt.split("```json")[1].split("```")[0]
    jsn = json.loads(json_txt)
    print(jsn)

@cache.cached(timeout=600, key_prefix="fetch_news")
def fetch_tech_news():
    news = []

    # make API request for news in JSON
    try:
        # make and validate get request
        response = requests.post(gemini_api_endpoint, headers=headers, json=params)
        response.raise_for_status()

        # parse json response
        try:
            json_txt = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            json_txt = json_txt.split("```json")[1].split("```")[0]

            article_list = json.loads(json_txt)
            if len(article_list) == 0:
                print("Received empty gemini response.")
            else:
                for article_json in article_list:
                    # Process article
                    article = {
                        "title": article_json.get("title", "No Title Available"),
                        "summary": article_json.get("summary", "No Summary Available"),
                        "date": article_json.get("date", "Date Not Available")
                    }

                    # If image missing, replace with placeholder
                    if "image_url" in article_json:
                        unsplash_params = {
                            "collections": "DR5Mh4ituPY"
                        }
                        img_response = requests.get(unsplash_api_endpoint, params=unsplash_params)

                        # error handling...

                        img_url = img_response.json()["urls"]["regular"]
                        article["image_url"] = img_url
                    #else:
                    #    article["image_url"] = article_json["image_url"]

                    # append article to news list
                    news.append(article)
        except ValueError as e:
            print(f"Error handling JSON: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        # then returns []

    return news

@app.route("/")
def index():
    articles = fetch_tech_news()
    return render_template("index.html", articles=articles)

if __name__=="__main__":
    app.run(debug=True, port=5001)
    #test()
