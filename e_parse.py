import os
import json
import lucene
from java.nio.file import Paths
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, Term
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
                    id_value = post_data.get("id", "")
                    doc.add(StringField("id", id_value, Field.Store.YES))
                    doc.add(TextField("title", post_data.get("title", ""), Field.Store.YES))
                    doc.add(TextField("author", post_data.get("author", ""), Field.Store.YES))
                    doc.add(TextField("url", post_data.get("url", ""), Field.Store.YES))
                    if "html_title" in post_data:
                        doc.add(TextField("html_title", post_data["html_title"], Field.Store.YES))
                    if "body" in post_data:
                        doc.add(TextField("body", post_data["body"], Field.Store.YES))
                    if "timestamp" in post_data:
                        doc.add(LongField("timestamp", int(post_data["timestamp"]), Field.Store.YES))
                    if "tags" in post_data:
                        tags = " ".join(post_data["tags"])
                        doc.add(TextField("tags", tags, Field.Store.YES))
                    writer.updateDocument(Term("id", id_value), doc)
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
    seen_ids = set()
    for hit in hits:
        doc = searcher.doc(hit.doc)
        doc_id = doc.get("id")
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            results.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "author": doc.get("author"),
                "url": doc.get("url"),
                "html_title": doc.get("html_title"),
                "body": doc.get("body"),
                "timestamp": doc.get("timestamp"),
                "tags": doc.get("tags"),
                "score": hit.score
            })
    return results

if __name__ == "__main__":
    input_files = ["reddit_posts_ucr_unique.json"]
    create_index(input_files)
    print("Indexing completed successfully.")