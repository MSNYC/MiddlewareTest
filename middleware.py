from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API keys from environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MIDDLEWARE_API_KEY = os.getenv("MIDDLEWARE_API_KEY")

# Create a Flask app
app = Flask(__name__)

# Define the root endpoint for handling requests from GPT
@app.route('/', methods=['POST'])
def fetch_news():
    try:
        # Verify the middleware API key
        request_api_key = request.headers.get("X-API-KEY")
        if request_api_key != MIDDLEWARE_API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Parse the incoming request data
        gpt_request = request.json
        query = gpt_request.get("q", "")
        search_in = gpt_request.get("searchIn", None)
        from_date = gpt_request.get("from", None)
        to_date = gpt_request.get("to", None)
        language = gpt_request.get("language", "en")
        sort_by = gpt_request.get("sortBy", "publishedAt")

        # Build the parameters for the NewsAPI request
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "apiKey": NEWS_API_KEY
        }

        # Add optional parameters if provided
        if search_in:
            params["searchIn"] = search_in
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        # Make the request to the NewsAPI
        response = requests.get("https://newsapi.org/v2/everything", params=params)
        
        # Handle any errors from NewsAPI
        if response.status_code != 200:
            return jsonify({"status": "error", "message": response.json().get("message", "Unknown error")}), response.status_code

        # Extract and format the articles for GPT
        news_data = response.json()
        formatted_articles = [
            {
                "source": {"name": article.get("source", {}).get("name")},
                "author": article.get("author"),
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "urlToImage": article.get("urlToImage"),
                "publishedAt": article.get("publishedAt"),
                "content": article.get("content")
            }
            for article in news_data.get("articles", [])
        ]

        # Return the response to GPT
        return jsonify({
            "status": "ok",
            "totalResults": news_data.get("totalResults", 0),
            "articles": formatted_articles
        })
    except Exception as e:
        # Catch unexpected errors
        return jsonify({"status": "error", "message": str(e)}), 500

# Run the app locally (Render will manage this in production)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)