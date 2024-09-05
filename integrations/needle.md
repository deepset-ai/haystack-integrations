---
layout: integration
name: Needle
description: Use Needle document store and retriever in Haystack.
authors:
    - name: Needle Team
      socials:
        twitter: needlexAI
        linkedin: needlexai
pypi: https://pypi.org/project/needle-haystack-ai
repo: https://github.com/JANHMS/needle-haystack
type: Document Store
report_issue: https://github.com/JANHMS/needle-haystack/issues
logo: /logos/needle.png
version: Haystack 2.x
---

# Needle RAG tools for Haystack

[![PyPI - Version](https://img.shields.io/pypi/v/needle-haystack-ai.svg)](https://pypi.org/project/needle-haystack-ai)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/needle-haystack-ai.svg)](https://pypi.org/project/needle-haystack-ai)

This package provides `NeedleDocumentStore` and `NeedleEmbeddingRetriever` component for use in Haystack projects.

## Usage ⚡️

Get started by installing the package via `pip`.

```bash
pip install needle-haystack-ai
```

### API Keys

We will show you building a common RAG pipeline using Needle tools and OpenAI generator.
For using these tools you must set your environment variables, `NEEDLE_API_KEY` and `OPENAI_API_KEY` respectively.

You can get your Needle API key from from [Developer settings](https://needle-ai.com/dashboard/settings).

### Example Pipeline 🧱

In Needle document stores are called collections. For detailed information, see our [docs](https://docs.needle-ai.com).
You can create a reference to your Needle collection using `NeedleDocumentStore` and use `NeedleEmbeddingRetriever` to retrieve documents from it.

```python
from needle_haystack import NeedleDocumentStore, NeedleEmbeddingRetriever

document_store = NeedleDocumentStore(collection_id="<your-collection-id>")
retriever = NeedleEmbeddingRetriever(document_store=document_store)
```

Use the retriever in a Haystack pipeline. Example:

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

prompt_template = """
Given the following retrieved documents, generate a concise and informative answer to the query:

Query: {{query}}
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

Answer:
"""

prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator()

# Add components to pipeline
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", llm)

# Connect the components
pipeline.connect("retriever", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")
```

Run your RAG pipeline:

```python
prompt = "What is the topic of the news?"

result = basic_rag_pipeline.run({
    "retriever": {"text": prompt},
    "prompt_builder": {"query": prompt}
})

# Print final answer
print(result['llm']['replies'][0])
```

# Support 📞

For detailed guides, take a look at our [docs](https://docs.needle-ai.com). If you have questions or requests you can contact us in our [Discord channel](https://discord.gg/JzJcHgTyZx). 
