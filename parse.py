import json
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory

# Initialize the JVM for PyLucene
lucene.initVM()

def create_index(json_file, index_dir):
    # Create a directory to store the index
    directory = SimpleFSDirectory(Paths.get(index_dir))

    # Create an analyzer to process the text
    analyzer = StandardAnalyzer()

    # Create an index writer configuration
    config = IndexWriterConfig(analyzer)

    # Create the index writer
    writer = IndexWriter(directory, config)

    try:
        # Parse the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return

    # Check if data is a list
    if not isinstance(data, list):
        print("JSON data is not a list of objects")
        return

    # Iterate over the JSON objects and index them
    for obj in data:
        doc = Document()
        # Add fields from the JSON object to the Lucene document
        if "username" in obj:
            doc.add(TextField("username", obj["username"], Field.Store.YES))
        if "timestamp" in obj:
            doc.add(TextField("timestamp", str(obj["timestamp"]), Field.Store.YES))
        if "body" in obj:
            doc.add(TextField("body", obj["body"], Field.Store.YES))
        if "title" in obj:
            doc.add(TextField("title", obj["title"], Field.Store.YES))
        if "author" in obj:
            doc.add(TextField("author", obj["author"], Field.Store.YES))
        if "url" in obj:
            doc.add(StringField("url", obj["url"], Field.Store.YES))
        # Add other fields as needed
        writer.addDocument(doc)

    # Commit and close the writer
    writer.commit()
    writer.close()

# Example paths
json_file = "reddit_posts_ucr.json"
index_dir = "/indexing"
create_index(json_file, index_dir)
