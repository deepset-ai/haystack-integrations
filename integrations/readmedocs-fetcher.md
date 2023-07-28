---
layout: integration
name: ReadMeDocs Fetcher
description: Fetch documentdation pages from ReadMe docs sites.
authors:
    - name: Tuana Çelik
      socials:
        github: tuanacelik
        twitter: tuanacelik
        linkedin: tuanacelik
    - name: Silvano Cerza
      socials:
        github: silvanocerza
        linkedin: silvanocerza
pypi: https://pypi.org/project/readmedocs-fetcher-haystack/
repo: https://github.com/tuanacelik/readmedocs-fetcher-haystack
type: Custom Node
report_issue: https://github.com/tuanacelik/readmedocs-fetcher-haystack/issues
---

This custom component for Haystack is designed to fetch documentation pages from the [ReadMe](https://readme.com/) documentation you have access to. It uses a `MarkdownConverter` to convert all of your documentation pages to a list of Haystack `Documents`. You can use this node as a standalone node or within an indexing pipeline. 

## Installation

```bash
pip install readmedocs-fetcher-haystack
```

## Usage

1. To initialize a `ReadmeDocsFetcher` you have to provide an `api_key` paramter. This is your ReadMe Docs API Key.
2. There are 3 optional parameters to initialize the `ReadmeDocsFetcher`
    - `slug`: To fetch a single defined page from your documentation. E.g. if you have want to fetch 'https://docs.haystack.deepset.ai/docs/installation' the slug would be `installation`. If not set, all of the available pages will be fetched.
    - `version`: If not set, the latest stable version of tour docs will be fethed. 
    - `markdown_converter`: When documents are fetched from ReadMe, temporary `.md` files are created and we use a [`MakrdownConverter`](https://docs.haystack.deepset.ai/reference/file-converters-api#markdownconverter) to create a list of haystack `Documents`. If not provided at initialization, the a `MarkdownConverter` with the default parameters is used.

### Standalone
```python
import os
from dotenv import load_dotenv
from haystack.nodes import MarkdownConverter

load_dotenv()
README_API_KEY = os.getenv('README_API_KEY')

converter = MarkdownConverter(remove_code_snippets=False)
readme_fetcher = ReadmeDocsFetcher(api_key=README_API_KEY, markdown_converter=converter)
readme_fetcher.fetch_docs()
```

To fetch a single doc from a specific version:
```python
readme_fetcher.fetch_docs(slug="nodes_overview", version="v1.18")
```
### In a Pipeline

```python
import os
from dotenv import load_dotenv
from haystack import Pipeline
from haystack.nodes import MarkdownConverter, PreProcessor
from haystack.document_stores import InMemoryDocumentStore
load_dotenv()
README_API_KEY = os.getenv('README_API_KEY')

converter = MarkdownConverter(remove_code_snippets=False)
readme_fetcher = ReadmeDocsFetcher(api_key=README_API_KEY, markdown_converter=converter)

preprocessor = PreProcessor()
doc_store = InMemoryDocumentStore()

pipe = Pipeline()
pipe.add_node(component=readme_fetcher, name="ReadmeFetcher", inputs=["File"])
pipe.add_node(component=preprocessor, name="Preprocessor", inputs=["ReadmeFetcher"])
pipe.add_node(component=doc_store, name="DocumentStore", inputs=["Preprocessor"])
pipe.run()
```

To fetch a single documentation page:
```python
pipe.run(params={"ReadmeFetcher":{"slug": "nodes_overview"}})
```
