import re
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

def extract_video_id(url: str) -> str | None:
    """
    Extract the 11-character YouTube video ID from various possible YouTube URL formats.
    Returns None if it fails to find an ID.
    """
    # Regex to match the typical patterns for YouTube IDs
    pattern = r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|embed)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/', methods=['GET'])
def home():
    return "YouTube Transcript API is running!", 200

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    """
    Accepts JSON input with a 'url' field containing the YouTube video link.
    Returns JSON with 'transcript' field containing the text of the transcript.
    Example JSON request:
      { "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    video_url = data['url']
    video_id = extract_video_id(video_url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # Fetch the transcript; returns a list of {text, start, duration} dicts
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine all text entries into one string
        transcript_text = " ".join([entry['text'] for entry in transcript_list])

        return jsonify({'transcript': transcript_text}), 200
    except Exception as e:
        # This will catch errors like "NoTranscriptFound" or "VideoUnavailable"
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # By default, Replit will set $PORT, so we listen on that
    app.run(host='0.0.0.0', port=8080)
