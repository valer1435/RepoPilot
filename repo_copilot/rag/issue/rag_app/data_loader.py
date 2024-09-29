import os
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.github import GithubRepositoryReader, GithubClient

from llama_index.readers.web import BeautifulSoupWebReader

from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import AsyncQdrantClient, QdrantClient

from embedding_factory import EmbeddingModelFactory


class DataLoader:
    def __init__(self, config):
        self.index = None
        client = QdrantClient(host="localhost", port=6333)
        aclient = AsyncQdrantClient(host="localhost", port=6333)
        self.embedding = EmbeddingModelFactory.get_embedding_model(config['Embedding']['provider'],
                                                                   **config['Embedding']['config'])
        self.github_client = GithubClient(
            github_token=os.environ["GITHUB_TOKEN"],
            verbose=True)
        self.vector_stores = {}
        for store in config['VectorStore']:
            vs = (QdrantVectorStore(
                store['name'],
                client=client,
                aclient=aclient,
                enable_hybrid=True,
                batch_size=20))

            pipeline = IngestionPipeline(
                transformations=[
                    SentenceSplitter(chunk_size=1000, chunk_overlap=500),
                    self.embedding
                ],
                vector_store=vs
            )
            self.vector_stores[store['name']] = {'vector_store': vs, 'pipeline': pipeline}

    def load_html(self, links, collection_name):
        loader = BeautifulSoupWebReader()
        try:
            documents = loader.load_data(urls=links)
            # Ingest directly into a vector db
            self.vector_stores[collection_name]['pipeline'].run(documents=documents, show_progress = True)
        except Exception as e:
            print(f"Error loading HTML from links: {e}")

    def load_site(self, address, collection_name):
        pages = get_all_pages(address)
        self.load_html(pages, collection_name)

    def load_code(self, owner, repo, branch, extensions, folders, collection_name):
        reader = GithubRepositoryReader(
            github_client=self.github_client,
            owner=owner, repo=repo,
            filter_directories=(folders, GithubRepositoryReader.FilterType.INCLUDE),
            filter_file_extensions=(extensions, GithubRepositoryReader.FilterType.INCLUDE),
            verbose=True)
        branch_documents = reader.load_data(branch=branch)
        self.vector_stores[collection_name]['pipeline'].run(documents=branch_documents, show_progress=True)
        print('Successfully downloaded documents')


def get_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def is_same_domain(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc and url.endswith('.html')


def get_all_pages(start_url):
    base_url = get_domain(start_url)
    visited = set()
    to_visit = [start_url]
    pages = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            continue

        visited.add(current_url)
        pages.append(current_url)

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            full_url = urljoin(current_url, link['href'])
            if is_same_domain(full_url, base_url) and full_url not in visited:
                to_visit.append(full_url)

    return pages
