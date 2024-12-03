---
layout: integration
name: Azure AI Search
description: Use Azure AI Search with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/azure-ai-search
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/azure-ai-search
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/aws.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Haystack 2.x](#haystack-2x)
    - [Installation](#installation)
    - [Usage](#usage)


## Overview

`AzureAIDocumentStore` supports an integration of [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search) which is an enterprise-ready search and retrieval system with [Haystack](https://haystack.deepset.ai/) by [deepset](https://www.deepset.ai).

The library allows using search indexes in Azure AI Search as a document store to build RAG-based applications on Azure, with native LLM integrations. To retrieve data from the documentstore, the integration supports three types of retrievers:

1. **Embedding Retrieval**: For vector-based searches.
2. **BM25 Retrieval**: Semantic retrieval utilizing the BM25 algorithm.
3. **Hybrid Retrieval**: Combining vector and BM25 retrieval methods for optimal results.

## Installation

Install the Azure AI Search integration:

```bash
pip install "azure-ai-search-haystack"
```

## Usage

You need to have an active Azure subscription with a deployed Azure AI Search service, to use `AzureAISearchDocumentStore`. 

```python
from haystack_integrations.document_stores.azure_ai_search import AzureAISearchDocumentStore
from haystack import Document

document_store = AzureAISearchDocumentStore(index_name="haystack-docs")
document_store.write_documents([
    Document(content="This is the first document."),
    Document(content="This is the second document.")
])
print(document_store.count_documents())
```

You can provide all supported parameters for `SearchIndex` for index creation during initialization of `AzureAISearchDocumentStore`.

You can enable semantic reranking in AzureAISearchDocumentStore by providing `SemanticSearch` configuration in `index_creation_kwargs` during initialization and calling it from one of the Retrievers. For more information, refer to the Azure AI tutorial on this feature.

### Connecting to Azure AI Search Index

To use the `AzureAISearchDocumentStore`, you need to provide a search service endpoint as an `AZURE_AI_SEARCH_ENDPOINT` and an API key as `AZURE_AI_SEARCH_API_KEY` for authentication. If the API key is not provided, the `DefaultAzureCredential` will attempt to authenticate you through the browser.
