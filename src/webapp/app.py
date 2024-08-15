from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv

async def create_app():
    from searching.search import ArticleSearcher # has to be here, need to initialize the chroma client/db before importing
    searcher_instance = ArticleSearcher()
    
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            query = request.form['query']
            results = searcher_instance.search_for_articles(query)
            return render_template('results.html', results=results, query=query)
        return render_template('search_bar.html')

    return app
