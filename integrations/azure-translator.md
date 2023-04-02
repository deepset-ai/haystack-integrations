---
name: Azure Translate Node
description: TranslateAnswer and TranslateQuery Nodes that use the Azure Translate endpoint
authors:
    - name: recrudesce (Russ)
      socials:
        github: recrudesce
        twitter: recrudesce
pypi:
repo: https://github.com/recrudesce/haystack_translate_node
type: Custom Node
report_issue: https://github.com/recrudesce/haystack_translate_node/issues
---

## Include in your pipeline as follows:
git clone the repo somewhere, change to the directory, then `pip install '.'`

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