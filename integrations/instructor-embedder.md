---
layout: integration
name: INSTRUCTOR Embedders
description: A component for computing embeddings using INSTRUCTOR embedding models - built for Haystack 2.0.
authors:
    - name: Ashwin Mathur
      socials:
        github: awinml
        twitter: awinml
        linkedin: ashwin-mathur-ds
    - name: Varun Mathur
      socials:
        github: vrunm
        twitter: vrunmnlp
        linkedin: varun-mathur-ds
pypi: https://pypi.org/project/instructor-embedders-haystack/
repo: https://github.com/deepset-ai/haystack-extras/tree/main/components/instructor-embedders
type: Custom Node
report_issue: https://github.com/deepset-ai/haystack-extras/issues
version: Haystack 2.0
---

[![PyPI - Version](https://img.shields.io/pypi/v/instructor-embedders-haystack.svg)](https://pypi.org/project/instructor-embedders-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/instructor-embedders-haystack.svg)](https://pypi.org/project/instructor-embedders-haystack)


This custom component for Haystack 2.0 can be used to create embeddings using the [INSTRUCTOR Embedding Models](https://instructor-embedding.github.io/). 


**INSTRUCTOR** is an instruction-finetuned text embedding model that can generate text embeddings tailored to any task (e.g., classification, retrieval, clustering, text evaluation, etc.) and domains (e.g., science, finance, etc.) ***by simply providing the task instruction, without any finetuning***. INSTRUCTOR achieves SOTA on 70 diverse embedding tasks ([MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)). For more details, check out [the paper](https://arxiv.org/abs/2212.09741) and [project page](https://instructor-embedding.github.io/). The model checkpoints can be found on [HuggingFace](https://huggingface.co/hkunlp?search_models=instructor).

The INSTRUCTOR models can be used to create domain-specific and task-aware embeddings, by passing an instruction along with the text to be encoded.

#### Unified Template for Creating Instructions
To create customized embeddings for specific sentences, you should follow the unified template to write instructions: 

        Represent the 'domain' 'text_type' for 'task_objective':  

* `domain` is optional, and it specifies the domain of the text, e.g., science, finance, medicine, etc.
* `text_type` is required, and it specifies the encoding unit, e.g., sentence, document, paragraph, etc.
* `task_objective` is optional, and it specifies the objective of embedding, e.g., retrieve a document, classify the sentence, etc.

**Example:**
1. **Document Text** - 'Capitalism has been dominant in the Western world since the end of feudalism, but most feel that the term "mixed economies" more precisely describes most contemporary economies, due to their containing both private-owned and state-owned enterprises. In capitalism, prices determine the demand-supply scale. For example, higher demand for certain goods and services lead to higher prices and lower demand for certain goods lead to lower prices.'  
    **Document Embedding Instruction** - 'Represent the Wikipedia document for retrieval:'

    **Query** - 'In a mixed economy, what are the key factors that determine whether a particular enterprise is privately owned or state-owned?'  
    **Query Embedding Instruction** - 'Represent the Wikipedia question for retrieving supporting documents:'

2. **Document Text** - 'The Federal Reserve on Wednesday raised its benchmark interest rate. The funds rose less than 0.5 per cent on Friday.'  
    **Document Embedding Instruction** - 'Represent the Financial statement:'

    **Query** - 'What was the impact of the interest rate hike?'  
    **Query Embedding Instruction** - 'Represent the Financial question:'


This component contains:
- `InstructorTextEmbedder`, a component that embeds a list of strings into a list of vectors.
- `InstructorDocumentEmbedder`, a component that embeds a list of Haystack `Documents`. The embedding of each `Document` is stored in the `embedding` field of the `Document`.

You can use these embedders as a standalone component or within an indexing pipeline. 

## Installation
To use this component, install the [`instructor-embedders-haystack`](https://pypi.org/project/instructor-embedders-haystack/) package.

```bash
pip install instructor-embedders-haystack
```

## Usage

1. To initialize the `InstructorTextEmbedder` or `InstructorDocumentEmbedder` you need to pass Local path or name of the model in Hugging Face's model hub, such as `'hkunlp/instructor-base'`, using the  `model_name_or_path` parameter.
2. The instruction string to be used while computing domain-specific embeddings needs to be passed using the `instruction` parameter.


### Using the Text Embedder

```python
from instructor_embedders.instructor_text_embedder import InstructorTextEmbedder

# Example text from the Amazon Reviews Polarity Dataset (https://huggingface.co/datasets/amazon_polarity)
text = "It clearly says online this will work on a Mac OS system. The disk comes and it does not, only Windows. Do Not order this if you have a Mac!!"
instruction = (
    "Represent the Amazon comment for classifying the sentence as positive or negative"
)

text_embedder = InstructorTextEmbedder(
    model_name_or_path="hkunlp/instructor-base", instruction=instruction,
    device="cpu"
)
```

### Using the Document Embedder

```python
from instructor_embedders.instructor_document_embedder import InstructorDocumentEmbedder
from haystack.preview.dataclasses import Document


doc_embedding_instruction = "Represent the Medical Document for retrieval:"

doc_embedder = InstructorDocumentEmbedder(
    model_name_or_path="hkunlp/instructor-base",
    instruction=doc_embedding_instruction,
    batch_size=32,
    device="cpu",
)

doc_embedder.warm_up()

# Text taken from PubMed QA Dataset (https://huggingface.co/datasets/pubmed_qa)
document_list = [
    Document(
        text="Oxidative stress generated within inflammatory joints can produce autoimmune phenomena and joint destruction. Radical species with oxidative activity, including reactive nitrogen species, represent mediators of inflammation and cartilage damage.",
        metadata={
            "pubid": "25,445,628",
            "long_answer": "yes",
        },
    ),
    Document(
        text="Plasma levels of pancreatic polypeptide (PP) rise upon food intake. Although other pancreatic islet hormones, such as insulin and glucagon, have been extensively investigated, PP secretion and actions are still poorly understood.",
        metadata={
            "pubid": "25,445,712",
            "long_answer": "yes",
        },
    ),
    Document(
        text="Disturbed sleep is associated with mood disorders. Both depression and insomnia may increase the risk of disability retirement. The longitudinal links among insomnia, depression and work incapacity are poorly known.",
        metadata={
            "pubid": "25,451,441",
            "long_answer": "yes",
        },
    ),
]

result = doc_embedder.run(document_list)
print(f"Document Text: {result['documents'][0].text}")
print(f"Document Embedding: {result['documents'][0].embedding}")
print(f"Embedding Dimension: {len(result['documents'][0].embedding)}")
```

### Using the Embedders in a Semantic Search Pipeline

```python
# Import necessary modules and classes
from haystack.preview.document_stores import MemoryDocumentStore
from haystack.preview.dataclasses import Document
from haystack.preview import Pipeline
from haystack.preview.components.writers import DocumentWriter
from haystack.preview.components.retrievers import MemoryEmbeddingRetriever
from datasets import load_dataset

# Import custom INSTRUCTOR Embedders
from instructor_embedders.instructor_document_embedder import InstructorDocumentEmbedder
from instructor_embedders.instructor_text_embedder import InstructorTextEmbedder

# Initialize a MemoryDocumentStore, which will be used to store and retrieve documents
# It uses cosine similarity for document embeddings comparison
doc_store = MemoryDocumentStore(embedding_similarity_function="cosine")

# Define an instruction for document embedding
doc_embedding_instruction = "Represent the News Article for retrieval:"
# Create an InstructorDocumentEmbedder instance with specified parameters
doc_embedder = InstructorDocumentEmbedder(
    model_name_or_path="hkunlp/instructor-base",
    instruction=doc_embedding_instruction,
    batch_size=32,
    device="cpu",
)
# Warm up the embedder (loading the pre-trained model)
doc_embedder.warm_up()

# Create an indexing pipeline
indexing_pipeline = Pipeline()
# Add the document embedder component to the pipeline
indexing_pipeline.add_component(instance=doc_embedder, name="DocEmbedder")
# Add a DocumentWriter component to the pipeline that writes documents to the Document Store
indexing_pipeline.add_component(
    instance=DocumentWriter(document_store=doc_store), name="DocWriter"
)
# Connect the output of DocEmbedder to the input of DocWriter
indexing_pipeline.connect(connect_from="DocEmbedder", connect_to="DocWriter")

# Load the 'XSum' dataset from HuggingFace (https://huggingface.co/datasets/xsum)
dataset = load_dataset("xsum", split="train")

# Create Document objects from the dataset and add them to the document store using the indexing pipeline
docs = [
    Document(
        text=doc["document"],
        metadata={
            "summary": doc["summary"],
            "doc_id": doc["id"],
        },
    )
    for doc in dataset
]
indexing_pipeline.run({"DocEmbedder": {"documents": docs}})

# Print the first document and its embedding from the document store
print(doc_store.filter_documents()[0])
print(doc_store.filter_documents()[0].embedding)

# Define an instruction for query embedding
query_embedding_instruction = (
    "Represent the news question for retrieving supporting articles:"
)
# Create an InstructorTextEmbedder instance for query embedding
text_embedder = InstructorTextEmbedder(
    model_name_or_path="hkunlp/instructor-base",
    instruction=query_embedding_instruction,
    device="cpu",
)
# Load the text embedding model
text_embedder.warm_up()

# Create a query pipeline
query_pipeline = Pipeline()
# Add the text embedder component to the pipeline
query_pipeline.add_component("TextEmbedder", text_embedder)
# Add a MemoryEmbeddingRetriever component to the pipeline that retrieves documents from the doc_store
query_pipeline.add_component(
    "Retriever", MemoryEmbeddingRetriever(document_store=doc_store)
)
# Connect the output of TextEmbedder to the input of Retriever
query_pipeline.connect("TextEmbedder", "Retriever")

# Run the query pipeline with a sample query text
results = query_pipeline.run(
    {
        "TextEmbedder": {
            "text": "What were the concerns expressed by Jeanette Tate regarding the response to the flooding in Newton Stewart?"
        }
    }
)

# Print information about retrieved documents
for doc in results["Retriever"]["documents"]:
    print(f"Text:\n{doc.text[:150]}...\n")
    print(f"Metadata: {doc.metadata}")
    print(f"Score: {doc.score}")
    print("-" * 10 + "\n")
```

## License

`instructor-embedders-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.




