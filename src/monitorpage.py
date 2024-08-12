from flask import Flask, render_template, jsonify
from analyse_articles import start_analysis, shared_state
import asyncio
import threading

app = Flask(__name__)

def run_analysis_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_analysis())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_analysis')
def start_analysis_route():
    if not hasattr(app, 'analysis_thread') or not app.analysis_thread.is_alive():
        app.analysis_thread = threading.Thread(target=run_analysis_in_thread)
        app.analysis_thread.start()
        return 'Analysis started'
    return 'Analysis already running'

@app.route('/status')
def status():
    return jsonify({
        'total_success': shared_state.total_success,
        'total_failure': shared_state.total_failure,
        'elapsed_time': shared_state.elapsed_time,
        'articles_per_second': shared_state.articles_per_second,
        'task_stats': [{'success': stats.success_count, 'failure': stats.failure_count} 
                       for stats in shared_state.task_stats],
        'total_articles': shared_state.total_articles,
        'progress': (shared_state.total_success + shared_state.total_failure) / shared_state.total_articles if shared_state.total_articles > 0 else 0
    })

if __name__ == '__main__':
    app.run(debug=True)