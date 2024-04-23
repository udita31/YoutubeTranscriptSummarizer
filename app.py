from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

def extract_video_id(video_url):
    if 'youtube.com/watch' in video_url or 'youtu.be' in video_url:
        video_id = video_url.split('/')[-1]  
        if 'watch' in video_id:
            video_id = video_id.split('=')[-1]
        return video_id

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/link', methods=['GET', 'POST'])
def link():
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = extract_video_id(video_url)
        
        if video_id:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            if not transcript:
                print("Transcript not available for the given video.")
            else:
                result = ""
                for i in transcript:
                    result += ' ' + i['text']

                return render_template('transcript.html', transcript=result)
    
    return render_template('link.html')

@app.route('/transcript', methods=['GET', 'POST'])
def show_transcript():
    transcript = request.form.get('transcript')  # Get transcript content from POST request
    
    # If the transcript content is available from the POST request, display it on the page
    if transcript:
        return render_template('transcript.html', transcript=transcript)

    # If there's no transcript content from the POST request, render an empty transcript.html page
    return render_template('transcript.html', transcript='')

@app.route('/summary', methods=['POST'])
def generate_summary():
    if request.method == 'POST':
        transcript = request.form.get('transcript')
        summarizer = pipeline('summarization')

        # Split the transcript into smaller chunks
        chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 1000)]

        summarized_text = []
        for chunk in chunks:
            summarized = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summarized_text.append(summarized[0]['summary_text'])

        summary = ' '.join(summarized_text)
        
        return render_template('summary.html', summary=summary)
    
    return render_template('summary.html', summary='')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
