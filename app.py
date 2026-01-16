from flask import Flask, render_template, request, redirect, url_for
from extractors import ExtractorFactory

app = Flask(__name__)

# Default source
DEFAULT_SOURCE = "otakudesu"

@app.context_processor
def inject_globals():
    return {
        'sources': ExtractorFactory.list_extractors(),
        'current_source': request.args.get('source', request.view_args.get('source', DEFAULT_SOURCE) if request.view_args else DEFAULT_SOURCE)
    }

@app.route('/')
def index():
    source = request.args.get('source', DEFAULT_SOURCE)
    # sources is injected by context_processor
    return render_template('index.html', source=source)

@app.route('/cust_search', methods=['POST'])
def search_anime():
    query = request.form.get('search')
    source = request.form.get('source', DEFAULT_SOURCE)
    if query:
        return redirect(url_for('search_results', source=source, query=query))
    return redirect(url_for('index', source=source))

@app.route('/search/<source>/<query>')
def search_results(source, query):
    extractor = ExtractorFactory.get_extractor(source)
    if not extractor:
        return "Source not found", 404
        
    results = extractor.search(query)
    return render_template('index.html', results=results, query=query, source=source)

@app.route('/anime/<source>/<path:url>')
def anime_details(source, url):
    extractor = ExtractorFactory.get_extractor(source)
    if not extractor:
        return "Source not found", 404

    # Fix: ensure URL is correctly reconstructed if it was partial or modified
    # In search_results, we passed the full URL or identifying ID.
    
    episodes = extractor.get_episodes(url)
    return render_template('anime.html', episodes=episodes, anime_url=url, source=source)

@app.route('/watch/<source>/<path:url>')
def watch_episode(source, url):
    extractor = ExtractorFactory.get_extractor(source)
    if not extractor:
        return "Source not found", 404
        
    stream_data = extractor.get_stream_url(url)
    return render_template('watch.html', stream=stream_data, episode_url=url, source=source)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
