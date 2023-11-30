---
layout: integration
name: OpenAI
description: Use OpenAI Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/openai.png
---

You can use [OpenAI Models](https://openai.com/) in your Haystack pipelines with the [EmbeddingRetriever](https://docs.haystack.deepset.ai/docs/retriever#embedding-retrieval-recommended), [PromptNode](https://docs.haystack.deepset.ai/docs/prompt_node), and [WhisperTranscriber](https://docs.haystack.deepset.ai/docs/whisper_transcriber)

## Installation

```bash
pip install farm-haystack
```

## Usage

You can use OpenAI models in various ways:

### Embedding Models

To use embedding models from OpenAI, initialize an `EmbeddingRetriever` with the model name and OpenAI API key. You can then use this `EmbeddingRetriever` in an indexing pipeline to create OpenAI embeddings for documents and index them to a document store. 

Below is the example indexing pipeline with `PreProcessor`, `InMemoryDocumentStore` and  `EmbeddingRetriever`:

```python
from haystack.nodes import EmbeddingRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import Pipeline
from haystack.schema import Document

document_store = InMemoryDocumentStore(embedding_dim=1024)
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    embedding_model="ada", document_store=document_store, api_key=OPENAI_API_KEY
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=preprocessor, name="Preprocessor", inputs=["File"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["Preprocessor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["Retriever"])
indexing_pipeline.run(documents=[Document("This is my document")])
```

### Generative Models (LLMs) 

To use GPT models from OpenAI, initialize a `PromptNode` with the model name, OpenAI API key and the prompt template. You can then use this `PromptNode` in a question answering pipeline to generate answers based on the given context.  

Below is the example of generative questions answering pipeline using RAG with `EmbeddingRetriever` and  `PromptNode`:

```python
from haystack.nodes import PromptNode, EmbeddingRetriever
from haystack.pipelines import Pipeline

retriever = EmbeddingRetriever(
    embedding_model="babbage", document_store=document_store, api_key=OPENAI_API_KEY
)
prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo", 
    api_key=OPENAI_API_KEY, 
    default_prompt_template="deepset/question-answering"
)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
query_pipeline.run("YOUR_QUERY")
```

### Transcriber Models

To use Whisper models from OpenAI, initialize a `WhisperTranscriber`. To use Whisper locally, install it following the instructions on the Whisper [GitHub repo](https://github.com/openai/whisper). To use the API implementation, provide an API key. You can then use this `WhisperTranscriber` to transcribe audio files.

Below is the example of summarization pipeline with `WhisperTranscriber` and  `PromptNode`:

```python
from haystack.nodes import WhisperTranscriber, PromptNode
from haystack.pipelines import Pipeline

whisper = WhisperTranscriber(api_key=api_key)
prompt_node = PromptNode(
        model_name_or_path="gpt-4", 
        api_key=api_key,
        default_prompt_template="deepset/summarization"
)

pipeline = Pipeline()
pipeline.add_node(component=whisper, name="whisper", inputs=["File"])
pipeline.add_node(component=prompt_node, name="prompt", inputs=["whisper"])

output = pipeline.run(file_paths=["path/to/audio/file"])
```