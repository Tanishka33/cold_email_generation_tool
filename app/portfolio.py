import pandas as pd
# Ensure sqlite3 is available in environments where the stdlib sqlite is missing
try:
    import sqlite3  # noqa: F401
except Exception:  # pragma: no cover - environment specific
    import pysqlite3 as sqlite3  # type: ignore
    import sys
    sys.modules["sqlite3"] = sqlite3
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        # Persist locally so the collection survives across Streamlit app runs
        # Using a relative path works on Streamlit Cloud's ephemeral filesystem per deploy
        self.chroma_client = chromadb.PersistentClient(path=".chroma")

        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                # Chromadb 0.4.x expects lists for documents, metadatas, and ids
                self.collection.add(
                    documents=[str(row["Techstack"])],
                    metadatas=[{"links": str(row["Links"])}],
                    ids=[str(uuid.uuid4())],
                )

    def query_links(self, skills):
        # Query by skills list, flatten the returned metadatas and extract link strings
        res = self.collection.query(query_texts=list(skills) if isinstance(skills, (list, tuple, set)) else [str(skills)], n_results=2)
        metadatas = res.get("metadatas", [])  # shape: [[{...}, {...}], ...]
        links = []
        for group in metadatas:
            for m in group:
                link = m.get("links")
                if link:
                    links.append(link)
        return links