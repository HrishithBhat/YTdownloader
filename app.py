from flask import Flask, render_template, request, redirect, flash, Response, stream_with_context
from downloader import download_video
import os
import queue
import threading

app = Flask(__name__,
             template_folder='frontend/templates',
             static_folder='frontend/static'
            )
app.secret_key = 'your_secret_key'

# Thread-safe queue to send progress updates
progress_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        flash("❌ Please enter a YouTube URL.")
        return redirect('/')

    # Define progress hook inside the function
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            if percent:
                percent = percent.replace('[', '').replace(']', '')
                progress_queue.put(percent)

    # Define threaded download inside the function
    def threaded_download():
        try:
            download_video(url, progress_hook)
            progress_queue.put("DONE")
        except Exception as e:
            progress_queue.put(f"ERROR: {e}")

    # Start download in new thread
    threading.Thread(target=threaded_download).start()
    return redirect('/')

@app.route('/progress')
def progress():
    def event_stream():
        while True:
            percent = progress_queue.get()
            yield f"data: {percent}\n\n"
            if percent == "DONE" or percent.startswith("ERROR"):
                break

    return Response(stream_with_context(event_stream()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
