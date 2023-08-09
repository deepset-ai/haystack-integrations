---
layout: integration
name: Pinecone Document Store
description: Use an Pinecone database with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/farm-haystack
repo: https://github.com/deepset-ai/haystack
type: Document Store
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/pinecone.png
---

[Pinecone](https://www.pinecone.io/) is a fast and scalable vector database which you can use in Haystack pipelines with the [PineconeDocumentStore](https://docs.haystack.deepset.ai/docs/document_store#initialization)

For a detailed overview of all the available methods and settings for the `PineconeDocumentStore`, visit the Haystack [API Reference](https://docs.haystack.deepset.ai/reference/document-store-api#pineconedocumentstore)

## Installation

```bash
pip install farm-haystack[pinecone]
```

## Usage

To use Pinecone as your data storage for your Haystack LLM pipelines, you must have an account with Pinecone and an API Key. Once you have those, you can initialize a `PineconeDocumentStore` for Haystack:

```python
from haystack.document_stores import PineconeDocumentStore

document_store = PineconeDocumentStore(api_key='YOUR_API_KEY',
                                       similarity="cosine",
                                       embedding_dim=768)
```

### Writing Documents to PineconeDocumentStore

To write documents to your `PineconeDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.
For this step, you may make use of the available [FileConverters](https://docs.haystack.deepset.ai/docs/file_converters) and [PreProcessors](https://docs.haystack.deepset.ai/docs/preprocessor), as well as other [Integrations](/integrations) that might help you fetch data from other resources. Below is an example indexing pipeline that indexes your Markdown files into a Pinecone database.

#### Indexing Pipleine

```python
from haystack import Pipeline
from haystack.document_stores import PineconeDocumentStore
from haystack.nodes import MarkdownConverter, PreProcessor

document_store = PineconeDocumentStore(api_key='YOUR_API_KEY',
                                       similarity="cosine",
                                       embedding_dim=768)
converter = MarkdownConverter()
preprocessor = PreProcessor()

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["PreProcessor"])

indexing_pipeline.run(file_paths=["filename.md"])
```

### Using Pinecone in a Query Pipeline

Once you have documents in your `PineconeDocumentStore`, it's ready to be used in any Haystack pipeline. For example, below is a pipeline that makes use of a custom prompt that is designed to answer questions for the retrieved documents.

```python
from haystack import Pipeline
from haystack.document_stores import PineconeDocumentStore
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate

document_store = PineconeDocumentStore(api_key='YOUR_API_KEY',
                                       similarity="cosine",
                                       embedding_dim=768)
              
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")
prompt_template = PromptTemplate(prompt = """"Answer the following query based on the provided context. If the context does
                                              not include an answer, reply with 'I don't know'.\n
                                              Query: {query}\n
                                              Documents: {join(documents)}
                                              Answer: 
                                          """,
                                          output_parser=AnswerParser())
prompt_node = PromptNode(model_name_or_path = "gpt-4",
                         api_key = "YOUR_OPENAI_KEY",
                         default_prompt_template = prompt_template)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "What is Pinecone", params={"Retriever" : {"top_k": 5}})
```