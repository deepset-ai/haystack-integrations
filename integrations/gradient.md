---
layout: integration
name: Gradient
description: Gradient is an LLM development platform that offers simple web APIs for fine-tuning, embeddings, and inference on state-of-the-art open-source models.
authors:
  - name: Mateusz Haligowski
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/gradient-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/gradient
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/gradient.png
version: Haystack 2.0
---

**Table of Contents**
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Installation
Use `pip` to install the integration:

```console
pip install gradient-haystack
```
## Usage
Once installed, you will have access to a Generator and two Embedder objects. 
- `GradientDocumentEmbedder`: Use this component to create embeddings of documents. This is commonly used in indexing pipelines to store documents and their embeddings in document stores.
- `GradientTextEmbedder`: Use this component to create embeddings of text, such as queries. This is commonly used as the first component of query pipelines to create embeddings of the query.
- `GradientGenerator`: Use this component to query generative models with Gradient. This is commonly used in query pipelines to generate responses to queries.

### Use the GradientDocumentEmbedder
You can use embedding models with `GradientDocumentEmbedder`` to create embeddings of your documents. This is commonly used in indexing pipelines to write documents and their embeddings into a document store.

```python
import os

from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter

from gradient_haystack.embedders.gradient_document_embedder import GradientDocumentEmbedder

os.environ["GRADIENT_ACCESS_TOKEN"] = "Your Gradient Access Token"
os.environ["GRADIENT_WORKSPACE_ID"] = "Your Gradient Workspace id: "

documents = [
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=GradientDocumentEmbedder(), name="document_embedder")
indexing_pipeline.add_component(instance=DocumentWriter(document_store=InMemoryDocumentStore()), name="document_writer")
indexing_pipeline.connect("document_embedder", "document_writer")
indexing_pipeline.run({"document_embedder": {"documents": documents}})
```

### Use the GradientTextEmbedder and GradientGenerator
You can use embedding models with `GradientTextEmbedder` and generative models with `GradientGenerator`. These two are commonly used together in a query pipeline such as a retrievel-augmented generative (RAG) pipeline such as the one below. 

```python
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers import InMemoryEmbeddingRetriever

from gradient_haystack.embedders.gradient_text_embedder import GradientTextEmbedder
from gradient_haystack.generator.base import GradientGenerator

from getpass import getpass

prompt_template = """
Given these documents, answer the question.\nDocuments:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
\nQuestion: {{question}}
\nAnswer:
"""

gradient_access_token = os.environ.get("GRADIENT_ACCESS_TOKEN")

retriever = InMemoryEmbeddingRetriever(document_store)
prompt_builder = PromptBuilder(template=prompt_template)
embedder = GradientTextEmbedder(access_token=gradient_access_token)
generator = GradientGenerator(access_token=gradient_access_token, base_model_slug="llama2-7b-chat")

rag_pipeline = Pipeline()
rag_pipeline.add_component(instance=embedder, name="text_embedder")
rag_pipeline.add_component(
    instance=retriever, name="retriever"
)
rag_pipeline.add_component(instance=prompt_builder, name="prompt_builder")
rag_pipeline.add_component(instance=generator, name="llm")
rag_pipeline.add_component(instance=AnswerBuilder(), name="answer_builder")

rag_pipeline.connect("text_embedder", "retriever")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")

rag_pipeline.run(
        {
            "text_embedder": {"text": question},
            "prompt_builder": {"question": question},
            "answer_builder": {"query": question},
        }
    )
```

## Examples
You can find a full code example showing how to use the integration in [this Colab](https://colab.research.google.com/drive/1kE_NAKKgZztQJMbgm2esyTVkAxlrpGtd#scrollTo=coE-fMtTJ-Pp).

## License

`gradient-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
