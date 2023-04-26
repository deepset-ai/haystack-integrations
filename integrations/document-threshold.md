---
layout: integration
name: Document Threshold
description: This component filters documents based on a threshold percentage, ensuring only the documents above the threshold get passed down the pipeline.
authors:
    - name: recrudesce
      socials:
        github: recrudesce
        twitter: recrudesce
pypi: https://pypi.org/project/haystack-threshold-node/
repo: https://github.com/recrudesce/haystack_threshold_node
type: Custom Node
report_issue: https://github.com/recrudesce/haystack_threshold_node/issues
---
# haystack_threshold_node
This component filters documents based on a threshold percentage, ensuring only the documents above the threshold get passed down the pipeline.
This allows you to query your document store for a larger top_k, but then filter the results down to those which are above a set confidence score.

## Installation

`pip install haystack-threshold-node`

## Usage

Include it in your pipeline - example as follows:

```python
import logging
import re

from datasets import load_dataset
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser, BM25Retriever
from haystack.pipelines import Pipeline
from haystack_lemmatize_node import LemmatizeDocuments


logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

document_store = InMemoryDocumentStore(use_bm25=True)

dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
document_store.write_documents(dataset)

retriever = BM25Retriever(document_store=document_store, top_k=10)

lfqa_prompt = PromptTemplate(
    name="lfqa",
    prompt_text="Given the context please answer the question using your own words. Generate a comprehensive, summarized answer. If the information is not included in the provided context, reply with 'Provided documents didn't contain the necessary information to provide the answer'\n\nContext: {documents}\n\nQuestion: {query} \n\nAnswer:",
    output_parser=AnswerParser(),
)

prompt_node = PromptNode(
    model_name_or_path="text-davinci-003",
    default_prompt_template=lfqa_prompt,
    max_length=500,
    api_key="sk-OPENAIKEY",
)

# The value you pass for threshold is the lowest % score you will accept. Whole numbers only.
# In this example, the threshold is set to 80%.
threshold = DocumentThreshold(threshold=80) 

pipe = Pipeline()
pipe.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipe.add_node(component=threshold, name="Threshold", inputs=["Retriever"])
pipe.add_node(component=prompt_node, name="prompt_node", inputs=["Threshold"])

query = "What does the Rhodes Statue look like?"
  
output = pipe.run(query)

print(output['answers'][0].answer)
```
