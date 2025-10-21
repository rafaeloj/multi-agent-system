from langchain_community.document_loaders import WebBaseLoader
from typing import List

def get_url_content(urls: List[str]) -> str:
    loader = WebBaseLoader(web_paths=urls)
    raw_docs = loader.load()

    docs = []
    for d in raw_docs:
        content = d.metadata['source']
        print(f"Fetched content from: {content}")
        # print(f"Content length: {len(d.page_content)} characters")
        # print("-" * 40)
        # print(d.page_content[:500])  # Print first 500 characters
        # print("\n" + "=" * 80 + "\n")
        content += d.page_content
        docs.append(content)
    return docs
