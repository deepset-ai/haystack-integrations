---
layout: integration
name: Document Lemmatizer
description: A lemmatizing node for documents which can potentially reduce token use by up to 30%.
authors:
    - name: recrudesce
      socials:
        github: recrudesce
        twitter: recrudesce
    - name: Xceron
      socials:
        github: Xceron
repo: https://github.com/recrudesce/haystack_lemmatize_node
type: Custom Node
report_issue: https://github.com/recrudesce/haystack_lemmatize_node/issues
---
## What is Lemmatization
Lemmatization is a text pre-processing technique used in natural language processing (NLP) models to break a word down to its root meaning to identify similarities. For example, a lemmatization algorithm would reduce the word better to its root word, or lemme, good.

This node can be placed within a pipeline to lemmatize documents returned by a Retriever, prior to adding them as context to a prompt (for a PromptNode or similar).
The process of lemmatizing the document content can potentially reduce the amount of tokens used by up to 30%, without drastically affecting the meaning of the document.

![image](https://user-images.githubusercontent.com/6450799/230403871-d0299748-977c-4c9e-9d70-914d8ff2bf3b.png)

### Before Lemmatization:
![image](https://user-images.githubusercontent.com/6450799/230404198-a3ed6382-03b8-4ec6-b88d-4232560752f8.png)

### After Lemmatization:
![image](https://user-images.githubusercontent.com/6450799/230404246-a8488a57-73bd-4420-9f1b-8a080b84121b.png)

## How to Use

Clone the repo to a directory, change to that directory, then perform a `pip install '.'`.  This will install the package to your Python libraries.

Then, include it in your pipeline - example as follows:

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

retriever = BM25Retriever(document_store=document_store, top_k=2)

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

lemmatize = LemmatizeDocuments() # you can pass the `base_lang=XX` argument here too, where XX is a language as listed here: https://pypi.org/project/simplemma/

pipe = Pipeline()
pipe.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipe.add_node(component=lemmatize, name="Lemmatize", inputs=["Retriever"])
pipe.add_node(component=prompt_node, name="prompt_node", inputs=["Lemmatize"])

query = "What does the Rhodes Statue look like?"
  
output = pipe.run(query)

print(output['answers'][0].answer)
```

## Caveats
Sometimes lemmatization can be slow for large document content, but in the world of AI where we can potentially wait 30+ seconds for an LLM to respond (hello GPT-4), what's a couple more seconds?
