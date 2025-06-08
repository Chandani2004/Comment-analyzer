from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import googleapiclient.discovery
import re
import html

app = Flask(__name__)
CORS(app)

# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
Developer_key = "AIzaSyCxtQBXtVgBgnG1dz8PFzjza90jRBEw4-s"  # Replace with yours

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=Developer_key
)


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be\/|embed\/|watch\?v=|&v=)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

# Clean comment
def clean_comment(raw_comment):
    unescaped = html.unescape(raw_comment)
    unescaped = re.sub(r'<br\s*/?>', ' ', unescaped)
    cleaned = re.sub(r'<[^>]+>', '', unescaped)
    return cleaned.strip()

def get_youtube_comments(video_id, max_results=100):
    try:
        request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=max_results
        )
        response = request.execute()
        return [clean_comment(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
                for item in response.get("items", [])]
    except Exception as e:
        return {"error": str(e)}

def predict_sentiment(comments):
    results = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
    sentiment_comments = []

    for comment in comments:
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0:
            sentiment = "POSITIVE"
        elif polarity == 0:
            sentiment = "NEUTRAL"
        else:
            sentiment = "NEGATIVE"
        results[sentiment] += 1
        sentiment_comments.append({"comment": comment, "sentiment": sentiment})

    total = len(comments) or 1
    percentages = {
        "POSITIVE": results["POSITIVE"],
        "NEUTRAL": results["NEUTRAL"],
        "NEGATIVE": results["NEGATIVE"],
        "POSITIVE_PERCENT": (results["POSITIVE"] / total) * 100,
        "NEUTRAL_PERCENT": (results["NEUTRAL"] / total) * 100,
        "NEGATIVE_PERCENT": (results["NEGATIVE"] / total) * 100
    }

    return sentiment_comments, percentages

@app.route('/get_comments', methods=['POST'])
def get_comments():
    try:
        data = request.get_json(force=True)
        video_url = data.get("videoUrl")
        video_id = extract_video_id(video_url)

        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'})

        comments = get_youtube_comments(video_id)
        if isinstance(comments, dict) and "error" in comments:
            return jsonify({'error': comments['error']})

        sentiment_comments, sentiment_stats = predict_sentiment(comments)

        return jsonify({
            'sentiment_results': sentiment_comments,
            'sentiment_percentages': sentiment_stats,
            'total_comments': len(comments)
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)