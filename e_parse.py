import os
import json
import lucene
from java.nio.file import Paths
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser

# Initialize lucene and the JVM
lucene.initVM()

# Directory where the index will be stored
index_dir = "index"

def create_index(input_files):
    directory = FSDirectory.open(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(directory, config)
    
    for input_file in input_files:
        with open(input_file, 'r') as f:
            for line in f:
                try:
                    post_data = json.loads(line)
                    doc = Document()
                    doc.add(StringField("id", post_data.get("id", ""), Field.Store.YES))
                    doc.add(TextField("title", post_data.get("title", ""), Field.Store.YES))
                    doc.add(TextField("author", post_data.get("author", ""), Field.Store.YES))
                    doc.add(TextField("url", post_data.get("url", ""), Field.Store.YES))
                    if "html_title" in post_data:
                        doc.add(TextField("html_title", post_data["html_title"], Field.Store.YES))
                    writer.addDocument(doc)
                except json.JSONDecodeError:
                    continue
    writer.close()

def search_index(query_str):
    lucene.getVMEnv().attachCurrentThread()  # Ensure the JVM is attached to the current thread
    directory = FSDirectory.open(Paths.get(index_dir))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()
    query = QueryParser("title", analyzer).parse(query_str)
    hits = searcher.search(query, 10).scoreDocs
    results = []
    for hit in hits:
        doc = searcher.doc(hit.doc)
        results.append({
            "id": doc.get("id"),
            "title": doc.get("title"),
            "author": doc.get("author"),
            "url": doc.get("url"),
            "html_title": doc.get("html_title"),
            "score": hit.score
        })
    return results

if __name__ == "__main__":
    input_files = ["reddit_posts_ucr.json"]
    create_index(input_files)
    print("Indexing completed successfully.")
