---
layout: integration
name: Bright Data
description: Extract data from 45+ websites, get search engine results, and access geo-restricted content using Bright Data's web scraping services.
authors:
  - name: Bright Data
    socials:
      github: brightdata
      twitter: brightdata
      linkedin: https://www.linkedin.com/company/bright-data/
pypi: https://pypi.org/project/haystack-brightdata
repo: https://github.com/brightdata/haystack-brightdata
type: Data Ingestion
report_issue: https://github.com/brightdata/haystack-brightdata/issues
logo: /logos/brightdata.jpeg
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Bright Data Web Scraper](#brightdatawebscraper)
  - [Bright Data SERP](#brightdataserp)
  - [Bright Data Unlocker](#brightdataunlocker)
  - [RAG Pipeline Example](#rag-pipeline-example)
- [Supported Datasets](#supported-datasets)
- [License](#license)

## Overview

[Bright Data](https://brightdata.com) is the world's leading web data platform, providing enterprise-grade web scraping and data collection solutions. The Bright Data Haystack integration provides three powerful components for extracting and accessing web data:

**Key Features:**
- **Web Scraper**: Extract structured data from 45+ supported websites including Amazon, LinkedIn, Instagram, Facebook, TikTok, YouTube, and more
- **SERP API**: Get search engine results from Google, Bing, Yahoo with geo-targeting and language customization
- **Web Unlocker**: Access geo-restricted and bot-protected websites, bypass CAPTCHAs and anti-bot measures

**Use Cases:**
- E-commerce price monitoring and product data extraction
- Social media analytics and content monitoring
- Business intelligence and competitive analysis
- Search engine results collection for SEO/SEM
- Accessing geo-restricted content for research
- Building RAG (Retrieval-Augmented Generation) pipelines with real-time web data

You need to have a Bright Data account and API key to use this integration. You can sign up at [Bright Data](https://brightdata.com/) and get your [API token](https://docs.brightdata.com/api-reference/authentication).

## Installation

Install the Bright Data-Haystack integration:

```bash
pip install haystack-brightdata
```

## Usage

The integration provides three main components:

### Bright Data Web Scraper

Extract structured data from 45+ supported websites. This component uses Bright Data's Dataset API to scrape e-commerce sites, social media platforms, business intelligence sources, and more.

**Supported Categories:**
- **E-commerce**: Amazon, Walmart, eBay, Home Depot, Zara, Etsy, Best Buy
- **LinkedIn**: Person profiles, Company profiles, Jobs, Posts, People Search
- **Social Media**: Instagram, Facebook, TikTok, YouTube, X/Twitter, Reddit
- **Business Intelligence**: Crunchbase, ZoomInfo
- **Search & Commerce**: Google Maps, Google Shopping, App Stores, Zillow, Booking.com
- **Other**: GitHub, Yahoo Finance, Reuters

```python
from haystack_brightdata import BrightDataWebScraper
import os

# Set your API key
os.environ["BRIGHT_DATA_API_KEY"] = "your-api-key"

# Initialize the scraper
scraper = BrightDataWebScraper()

# Extract Amazon product data
result = scraper.run(
    dataset="amazon_product",
    url="https://www.amazon.com/dp/B08N5WRWNW"
)
print(result["data"])

# Extract LinkedIn profile data
result = scraper.run(
    dataset="linkedin_person_profile",
    url="https://www.linkedin.com/in/example-profile/"
)
print(result["data"])

# Extract Instagram profile data
result = scraper.run(
    dataset="instagram_profiles",
    url="https://www.instagram.com/username/"
)
print(result["data"])
```

**List all supported datasets:**

```python
from haystack_brightdata import BrightDataWebScraper

# Get all supported datasets
datasets = BrightDataWebScraper.get_supported_datasets()
for dataset in datasets:
    print(f"{dataset['id']}: {dataset['description']}")

# Get info about a specific dataset
info = BrightDataWebScraper.get_dataset_info("amazon_product")
print(f"Description: {info['description']}")
print(f"Required inputs: {info['inputs']}")
```

### Bright Data SERP

Execute search engine queries and get structured results from Google, Bing, Yahoo, and other search engines with geo-targeting and language customization.

```python
from haystack_brightdata import BrightDataSERP
import os

# Set your API key
os.environ["BRIGHT_DATA_API_KEY"] = "your-api-key"

# Initialize SERP component
serp = BrightDataSERP(
    default_search_engine="google",
    default_country="us",
    default_language="en"
)

# Execute a search query
result = serp.run(
    query="machine learning tutorials",
    num_results=20,
    search_type="web"
)
print(result)

# Search from a different country with different language
result = serp.run(
    query="inteligencia artificial",
    country="es",
    language="es",
    num_results=10
)
print(result)
```

### Bright Data Unlocker

Access geo-restricted and bot-protected websites. Bypass anti-bot measures, CAPTCHAs, and geographic restrictions.

```python
from haystack_brightdata import BrightDataUnlocker
import os

# Set your API key
os.environ["BRIGHT_DATA_API_KEY"] = "your-api-key"

# Initialize Web Unlocker
unlocker = BrightDataUnlocker(default_output_format="markdown")

# Access a website and get content as markdown
result = unlocker.run(
    url="https://example.com/restricted-content",
    output_format="markdown"
)
print(result["content"])

# Access from a specific country
result = unlocker.run(
    url="https://example.com",
    country="gb",
    output_format="html"
)
print(result)

# Get a screenshot
result = unlocker.run(
    url="https://example.com",
    output_format="screenshot"
)
# result contains base64-encoded screenshot
```

### RAG Pipeline Example

Build a Retrieval-Augmented Generation (RAG) pipeline using Bright Data to extract product data from Amazon and answer questions about products:

```python
import os
from haystack import Pipeline, Document
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import ChatMessage
from haystack_brightdata import BrightDataWebScraper
import json

# Set API keys
os.environ["BRIGHT_DATA_API_KEY"] = "brightdata-api-key"
os.environ["OPENAI_API_KEY"] = "openai-api-key"

# Initialize components
scraper = BrightDataWebScraper()
document_store = InMemoryDocumentStore()
docs_embedder = OpenAIDocumentEmbedder()
text_embedder = OpenAITextEmbedder()
retriever = InMemoryEmbeddingRetriever(document_store)
generator = OpenAIChatGenerator()

# Scrape product data from multiple Amazon products
product_urls = [
    "https://www.amazon.com/dp/B0DRWBJDLJ",
    "https://www.amazon.com/dp/B08B8M5JGN",
    "https://www.amazon.com/dp/B09WTTWH1R",
]

documents = []
for url in product_urls:
    result = scraper.run(dataset="amazon_product", url=url)

    # Parse the response - it should be a list of product dictionaries
    if isinstance(result["data"], str):
        product_data = json.loads(result["data"])
    else:
        product_data = result["data"]

    # Ensure we have a list
    if not isinstance(product_data, list):
        product_data = [product_data]

    # Convert product data to document
    for product in product_data:
        # Build content with all relevant product information
        content_parts = [
            f"Product: {product.get('title', 'N/A')}",
            f"Brand: {product.get('brand', 'N/A')}",
            f"Seller: {product.get('seller_name', 'N/A')}",
            f"Price: ${product.get('final_price', 'N/A')} {product.get('currency', '')}",
            f"Rating: {product.get('rating', 0)}/5",
            f"Reviews Count: {product.get('reviews_count', 0)}",
            f"Availability: {product.get('availability', 'N/A')}",
        ]

        # Add description if available
        if product.get('description'):
            content_parts.append(f"Description: {product.get('description')}")

        # Add features if available
        if product.get('features'):
            features_text = '\n  - '.join(product.get('features', []))
            content_parts.append(f"Features:\n  - {features_text}")

        # Add categories if available
        if product.get('categories'):
            categories_text = ' > '.join(product.get('categories', []))
            content_parts.append(f"Categories: {categories_text}")

        # Add delivery info if available
        if product.get('delivery'):
            delivery_text = ', '.join(product.get('delivery', []))
            content_parts.append(f"Delivery: {delivery_text}")

        # Add variations count if available
        if product.get('variations'):
            content_parts.append(f"Variations Available: {len(product.get('variations', []))}")

        content = '\n'.join(content_parts)

        documents.append(Document(
            content=content,
            meta={
                "url": product.get('url', url),
                "title": product.get('title', ''),
                "asin": product.get('asin', ''),
                "brand": product.get('brand', ''),
                "price": product.get('final_price', 0),
                "rating": product.get('rating', 0),
                "reviews_count": product.get('reviews_count', 0)
            }
        ))

# Embed and store documents
print("Indexing documents...")
embeddings = docs_embedder.run(documents)
document_store.write_documents(embeddings["documents"])

# Create RAG pipeline with ChatPromptBuilder
messages = [
    ChatMessage.from_system("You are a helpful shopping assistant. Answer questions about products based on the provided context."),
    ChatMessage.from_user("""
Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
""")
]

prompt_builder = ChatPromptBuilder(template=messages)

# Build pipeline
pipe = Pipeline()
pipe.add_component("embedder", text_embedder)
pipe.add_component("retriever", retriever)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)

# Connect components
pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

# Ask questions about the products
question = "Which product has the best rating?"
print(f"\nQuestion: {question}")

response = pipe.run({
    "embedder": {"text": question},
    "prompt_builder": {"question": question}
})

print(f"Answer: {response['llm']['replies'][0].text}")

# Ask more questions
questions = [
    "What are the price ranges of these products?",
    "Which product has the most reviews?",
    "What are the key features across all products?",
]

for question in questions:
    response = pipe.run({
        "embedder": {"text": question},
        "prompt_builder": {"question": question}
    })
    print(f"\nQuestion: {question}")
    print(f"Answer: {response['llm']['replies'][0].text}")
```

**SERP + RAG Pipeline Example:**

Use SERP API to find relevant web pages, then use Web Unlocker to extract content for a RAG pipeline:

```python
import os
from haystack import Pipeline, Document
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import ChatMessage
from haystack_brightdata import BrightDataSERP, BrightDataUnlocker
import json

# Set API keys
os.environ["BRIGHT_DATA_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

# Initialize components
serp = BrightDataSERP()
unlocker = BrightDataUnlocker(default_output_format="markdown",zone="unblocker")
document_store = InMemoryDocumentStore()
docs_embedder = OpenAIDocumentEmbedder()
text_embedder = OpenAITextEmbedder()
retriever = InMemoryEmbeddingRetriever(document_store)
generator = OpenAIChatGenerator(model="gpt-4")

# Search for information
search_query = "best practices for machine learning in production"
search_result = serp.run(query=search_query, num_results=5)
search_data = json.loads(search_result["results"])

# Debug: Print the structure of search results
print("Search data keys:", search_data.keys() if isinstance(search_data, dict) else type(search_data))
if isinstance(search_data, dict) and "organic" in search_data:
    print(f"Found {len(search_data.get('organic', []))} organic results")
    if search_data.get("organic"):
        print("First result keys:", search_data["organic"][0].keys())

# Extract URLs from search results
urls = []
for result in search_data.get("organic", [])[:5]:
    url = result.get("url") or result.get("link")
    if url:
        urls.append(url)
    else:
        print(f"Warning: No URL found in result: {result.keys()}")

# Fetch content from each URL
documents = []
print(f"\nFetching content from {len(urls)} URLs...")
for url in urls:
    if not url:
        print(f"Skipping empty URL")
        continue
    try:
        print(f"Fetching: {url}")
        result = unlocker.run(url=url, output_format="markdown")
        content = result["content"]
        documents.append(Document(
            content=content,
            meta={"url": url}
        ))
        print(f"✓ Successfully fetched {url}")
    except Exception as e:
        print(f"✗ Failed to fetch {url}: {e}")

# Embed and store documents
print(f"Indexing {len(documents)} documents...")
embeddings = docs_embedder.run(documents)
document_store.write_documents(embeddings["documents"])

# Create RAG pipeline with ChatPromptBuilder
messages = [
    ChatMessage.from_system("You are a knowledgeable AI assistant. Answer questions based on the provided web sources."),
    ChatMessage.from_user("""
Context from web sources:
{% for document in documents %}
    Source: {{ document.meta.url }}
    {{ document.content }}
{% endfor %}

Question: {{question}}
""")
]

prompt_builder = ChatPromptBuilder(template=messages)

# Build pipeline
pipe = Pipeline()
pipe.add_component("embedder", text_embedder)
pipe.add_component("retriever", retriever)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)

# Connect components
pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

# Ask questions
question = "What are the main challenges of deploying ML models in production?"
print(f"\nQuestion: {question}")

response = pipe.run({
    "embedder": {"text": question},
    "prompt_builder": {"question": question}
})

print(f"Answer: {response['llm']['replies'][0].text}")
```

## Supported Datasets

The `BrightDataWebScraper` component supports 45+ datasets across multiple categories:

**E-commerce (10 datasets):**
- amazon_product, amazon_product_reviews, amazon_product_search
- walmart_product, walmart_seller
- ebay_product, homedepot_products, zara_products, etsy_products, bestbuy_products

**LinkedIn (5 datasets):**
- linkedin_person_profile, linkedin_company_profile, linkedin_job_listings
- linkedin_posts, linkedin_people_search

**Instagram (4 datasets):**
- instagram_profiles, instagram_posts, instagram_reels, instagram_comments

**Facebook (4 datasets):**
- facebook_posts, facebook_marketplace_listings, facebook_company_reviews, facebook_events

**TikTok (4 datasets):**
- tiktok_profiles, tiktok_posts, tiktok_shop, tiktok_comments

**YouTube (3 datasets):**
- youtube_profiles, youtube_videos, youtube_comments

**Search & Commerce (6 datasets):**
- google_maps_reviews, google_shopping, google_play_store, apple_app_store
- zillow_properties_listing, booking_hotel_listings

**Business Intelligence (2 datasets):**
- crunchbase_company, zoominfo_company_profile

**Other (5 datasets):**
- reuter_news, github_repository_file, yahoo_finance_business, x_posts, reddit_posts

For detailed information about each dataset and its required parameters, use:

```python
from haystack_brightdata import BrightDataWebScraper

# List all datasets
datasets = BrightDataWebScraper.get_supported_datasets()
for dataset in datasets:
    print(f"{dataset['id']}: {dataset['description']}")
```

## License

`haystack-brightdata` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
