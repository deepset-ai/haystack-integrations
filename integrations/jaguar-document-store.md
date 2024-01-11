---
layout: integration
name: Jaguar Document Store
description: Use a Jaguar database with Haystack
authors:
    - name: deepset
      socials:
        github: https://github.com/fserv/jaguar-haystack
        twitter: 
        linkedin: 
pypi: https://pypi.org/project/jaguar-haystack
repo: https://github.com/fserv/jaguar-haystack
type: Document Store
report_issue: 
---

Haystack supports the use of [Jaguar](http://www.jaguardb.com/) as data storage for LLM pipelines, with the `JaguarDocumentStore`. You can choose to run Jaguar locally youself, or use cloud versions: multi-tenant, single-tenant multi-member, or single-tenant and single-member.

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
from jaguar_haystack.jaguar import JaguarDocumentStore

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

To write documents to your `JaguarDocumentStore`, create an indexing pipeline, or use the `write_documents()` function.

#### Indexing Pipeline

```python
from haystack import Pipeline
from haystack.nodes import EmbeddingRetriever, MarkdownConverter, PreProcessor

converter = MarkdownConverter()
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(document_store = document_store,
                               embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1")

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["PreProcessor"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])

indexing_pipeline.run(file_paths=["myfile.pdf"])
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

query_pipeline.run(query = "Where is the Bermuda Traingle? ", params={"Retriever" : {"top_k": 5}})
```
