from flask import Flask, request, render_template
import e_parse
import lucene

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    lucene.getVMEnv().attachCurrentThread()  # Ensure the JVM is attached to the current thread
    query = request.args.get('q')
    if query:
        results = e_parse.search_index(query)
        return render_template('results.html', query=query, results=results)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
    # If you want to use port 8080, change port=8888 to port=8080
