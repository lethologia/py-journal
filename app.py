from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

if not GEMINI_KEY or not UNSPLASH_KEY:
    raise OSError(f"Missing API Key. Gemini: {GEMINI_KEY}, Unsplash: {UNSPLASH_KEY}")

# unsplash api params
unsplash_api_endpoint = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_KEY}"

# configure gemini model
model = "gemini-1.5-flash"
gemini_api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"

# gemini request parameters
headers = {
    "Content-Type": "application/json"
}

system_instruction = {
    "parts": { 
        "text": "You are a journalist for a tech article which posts about the latest tech news. You cater primarily to engineers, and others with similar context"
    }
}

contents = {
    "parts": {
        "text": "What are 12 tech articles regarding news of the last month?"
    }
}

tools = [{
    "google_search_retrieval": {
        "mode": "MODE_DYNAMIC",
        "dynamic_threshold": 0.4
    }
}]

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

params = {
    "system_instruction": system_instruction,
    "contents": contents,
    "tools": tools,
    "generationConfig": gen_cfg
}

def fetch_tech_news():
    news = []

    # make API request for news in JSON
    try:
        # make and validate get request
        response = requests.get(gemini_api_endpoint, headers=headers, params=params)
        response.raise_for_status()

        # parse json response
        try:
            article_list = response.json()
            if len(article_list) != 0:
                print("Recieved empty gemini response.")
            else:
                for article_json in article_list:
                    # Process article
                    article = {
                        "title": article_json.get("title", "No Title Available"),
                        "summary": article_json.get("summary", "No Summary Available"),
                        "date": article_json.get("date", "Date Not Available")
                    }

                    # If image missing, replace with placeholder
                    if "image_url" not in article_json:
                        unsplash_params = {
                            "collections": "DR5Mh4ituPY"
                        }
                        img_response = requests.get(unsplash_api_endpoint, params=unsplash_params)

                        # error handling...

                        img_url = response.json()["urls"]["regular"]
                        article["image_url"] = img_url
                    else:
                        article["image_url"] = article_json["image_url"]

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
