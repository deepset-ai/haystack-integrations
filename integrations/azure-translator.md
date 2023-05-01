---
layout: integration
name: Azure Translate Nodes
description: TranslateAnswer and TranslateQuery Nodes that use the Azure Translate endpoint
authors:
    - name: recrudesce (Russ)
      socials:
        github: recrudesce
        twitter: recrudesce
pypi: https://pypi.org/project/haystack-translate-node/ 
repo: https://github.com/recrudesce/haystack_translate_node
type: Custom Node
report_issue: https://github.com/recrudesce/haystack_translate_node/issues
---

This package allows you to use the Azure translation endpoints to separately translate the query and the answer. It's good for scenarios where your dataset is in a different language to what you expect the user query to be in. This way, you will be able to translate the user query to the your dataset's language, and translate the answer back to the user's language.

## Installation
Run `pip install haystack-translate-node` to install the latest available version.

## Usage
Include in your pipeline as follows:

```python
from haystack_translate_node import TranslateAnswer, TranslateQuery

translate_query = TranslateQuery(api_key="<yourapikey>", location="<yourazureregion>", azure_translate_endpoint="<yourazureendpoint>", base_lang="en")
translate_answer = TranslateAnswer(api_key="<yourapikey>", location="<yourazureregion>", azure_translate_endpoint="<yourazureendpoint>", base_lang="en")

pipel = Pipeline()
pipel.add_node(component=translate_query, name="TranslateQuery", inputs=["Query"])
pipel.add_node(component=retriever, name="Retriever", inputs=["TranslateQuery"])
pipel.add_node(component=prompt_node, name="prompt_node", inputs=["Retriever"])
pipel.add_node(component=translate_answer, name="TranslateAnswer", inputs=["prompt_node"])
```

`location`, `azure_translate_endpoint`, and `base_lang` are optional, and will default to uksouth, https://api.cognitive.microsofttranslator.com/, and en respectively.

TranslateQuery will determine the language of the query, and assign it to the `in_lang` JSON value.

TranslateQuery will take the original query, in any language, and assign it to the `in_query` JSON value.

TranslateQuery will overwrite the original `query` JSON value with the translated English value

You can then query your `base_lang` corpus using the `query` value as normal using a standard Haystack Retriever node, which will place your results in `results`.

TranslateAnswer translate the `base_lang` result stored in results back to the language stored in `in_lang` and subsequently store it in the `out_answer` JSON value.
