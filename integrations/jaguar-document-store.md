---
layout: integration
name: Jaguar Document Store
description: Use a Jaguar database with Haystack
authors:
    - name: fserv
      socials:
        github: https://github.com/fserv/jaguar-haystack
        twitter: 
        linkedin: 
pypi: https://pypi.org/project/jaguar-haystack
repo: https://github.com/fserv/jaguar-haystack
type: Document Store
report_issue: https://github.com/fserv/jaguar-haystack/issues
---

Haystack supports the use of [Jaguar](http://www.jaguardb.com/) as data storage for LLM pipelines, with the `JaguarDocumentStore`. You can choose to run Jaguar locally yourself, or use cloud versions: multi-tenant, single-tenant multi-member, or single-tenant and single-member. The following documentation is aligned with the Haystack 2.0 framework.

For details on the available methods and parameters of the `JaguarDocumentStore`, check out [Documentation](http://www.jaguardb.com/support.html)

## Installation

```bash
docker pull jaguardb/jaguardb_with_http
docker run -d -p 8888:8888 -p 8080:8080 --name jaguardb_with_http  jaguardb/jaguardb_with_http
pip install -U jaguar-haystack
pip install -U jaguardb-http-client
```

## Usage

To use Jaguar as your data storage for your Haystack LLM pipelines, you should set it up running. Then, you can make a `JaguarDocumentStore`:

```python
from haystack_integrations.document_stores.jaguar import JaguarDocumentStore

url = "http://127.0.0.1:8080/fwww/"
pod = "vdb"
store = "haystack_test_store"
vector_index = "v"
vector_type = "cosine_fraction_float"
vector_dimension = 1536
document_store = JaguarDocumentStore(
    pod,
    store,
    vector_index,
    vector_type,
    vector_dimension,
    url,
)
```

### Writing Documents to JaguarDocumentStore

To write documents to your `JaguarDocumentStore`, you can use the `write_documents()` function or
create an indexing pipeline to load documents into the store.

#### Write Documents

```python
from haystack.dataclasses import Document

doc1 = Document(
    content="Return of King Lear",
    embedding=[0.9, 0.1, 0.4],
)

doc2 = Document(
    content="Slow Clouds",
    embedding=[0.4, 0.2, 0.8],
)

doc3 = Document(
    content="Green Machine",
    embedding=[0.1, 0.7, 0.5],
)

docs = [doc1, doc2, doc3]
document_store.write_documents(documents=docs)

```


#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.components.file_converters import TextFileToDocument
from haystack.components.writers import DocumentWriter

indexing = Pipeline()
indexing.add_component("converter", TextFileToDocument())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")
indexing.run({"converter": {"paths": file_paths}})

```

### Using Jaguar in a Query Pipeline

Once you saved documents in your `JaguarDocumentStore`, you can use a Haystack pipeline for query.

```python
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate

retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

prompt = """"Given the provided Documents, answer the Query. Make your answer detailed and long\n
             Query: {query}\n
             Documents: {join(documents)}
             Answer: 
         """
prompt_template = PromptTemplate(prompt = prompt, output_parser=AnswerParser())
prompt_node = PromptNode(model_name_or_path = "gpt-4",
                         api_key = "YOUR_OPENAI_KEY",
                         default_prompt_template = prompt_template)

query_pipeline = Pipeline()
query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

query_pipeline.run(query = "Where is the Bermuda Triangle? ", params={"Retriever" : {"top_k": 5}})
```
