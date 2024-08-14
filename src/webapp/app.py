from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from searching.search import search_for_articles

async def create_app():
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            query = request.form['query']
            results = search_for_articles(query)
            return render_template('results2.html', results=results, query=query)
        return render_template('try.html')

    return app
