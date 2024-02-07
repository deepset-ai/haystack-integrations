---
layout: integration
name: LM Format Enforcer
description: Use the LM Format Enforcer to enforce JSON Schema / Regex output of your Local Models.
authors:
  - name: noamgat
    socials:
      github: noamgat
      twitter: noamgat
pypi: https://pypi.org/project/lm-format-enforcer/
repo: https://github.com/noamgat/lm-format-enforcer
type: Model Provider
report_issue: https://github.com/noamgat/lm-format-enforcer/issues
logo: /logos/lmformatenforcer.png
version: Haystack 2.0
---

# LM Format Enforcer Haystack Integration Layer

Use the [LM Format Enforcer](https://github.com/noamgat/lm-format-enforcer)  to enforce JSON Schema / Regex output of your local models in your haystack pipelines.

Language models are able to generate text, but when requiring a precise output format, they do not always perform as instructed. Various prompt engineering techniques have been introduced to improve the robustness of the generated text, but they are not always sufficient. [LM Format Enforcer](https://github.com/noamgat/lm-format-enforcer) solves the issues by filtering the tokens that the language model is allowed to generate at every timestep, thus ensuring that the output format is respected, while minimizing the limitations on the language model.

### What is the LM Format enforcer?
![Solution at a glance](https://raw.githubusercontent.com/noamgat/lm-format-enforcer/main/docs/Intro.webp)



## Installation
Install the format enforcer via pip:  `pip install lm-format-enforcer`

## Usage
This integration supports both Haystack 1.x and Haystack 2.0:
- `LMFormatEnforcerPromptNode`: A Haystack 1.x `PromptNode` that activates the format enforcer.
- `LMFormatEnforcerLocalGenerator`: A Haystack 2.0 Generator component that activates the format enforcer.

Important note: LM Format Enforcer requires a LOCAL generator - currently only Local HuggingFace transformers are supported, vLLM suport is coming soon.

### Creating a CharacterLevelParser
The `CharacterLevelParser` is the class that connects the output parsing to the format enforcing. Two main parsers are available : `JsonSchemaParser` for JSON Schemas, and `RegexParser` for regular expressions.

We will start off by defining the format we want to decode, regardless of Haystack.

```python

from pydantic import BaseModel
from lmformatenforcer import JsonSchemaParser

class AnswerFormat(BaseModel):
    first_name: str
    last_name: str
    year_of_birth: int
    num_seasons_in_nba: int

parser = JsonSchemaParser(AnswerFormat.schema())
```
### Haystack 1.x Integration
<a target="_blank" href="https://colab.research.google.com/github/noamgat/lm-format-enforcer/blob/main/samples/colab_haystackv1_integration.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

To activate the the enforcer with Haystack V1, a `LMFormatEnforcerPromptNode` has to be used. 

Here is a simple example:
```python
from haystack.nodes import PromptModel
from lmformatenforcer.integrations.haystackv1 import LMFormatEnforcerPromptNode

question = 'Please give me information about {query}. You MUST answer using the following json schema: '
schema_json_str = AnswerFormat.schema_json().replace("{", "{{").replace("}", "}}")
question_with_schema = f'{question}{schema_json_str}'
prompt = get_prompt(question_with_schema)


model = PromptModel(model_name_or_path="meta-llama/Llama-2-7b-chat-hf")
prompt_node = LMFormatEnforcerPromptNode(model, prompt, character_level_parser=parser)

result = prompt_node(query='Michael Jordan')
print(result[0])

```
The model will be inferred with the format enforcer, and the output will look like this:

```
{
"first_name": "Michael",
"last_name": "Jordan",
"year_of_birth": 1963,
"num_seasons_in_nba": 15
}
```
For a full example, see the [example notebook](https://github.com/noamgat/lm-format-enforcer/blob/main/samples/colab_haystackv1_integration.ipynb)

### Haystack 2.0 Integration
<a target="_blank" href="https://colab.research.google.com/github/noamgat/lm-format-enforcer/blob/main/samples/colab_haystackv2_integration.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

To activate the the enforcer with Haystack V2, a `LMFormatEnforcerLocalGenerator` has to be used. 

Here is a simple example:
```python
from haystack.components.generators.hugging_face.hugging_face_local import HuggingFaceLocalGenerator
from lmformatenforcer.integrations.haystackv2 import LMFormatEnforcerLocalGenerator


question = 'Please give me information about Michael Jordan. You MUST answer using the following json schema: '
schema_json_str = AnswerFormat.schema_json()
prompt = f'{question}{schema_json_str}'


model = HuggingFaceLocalGenerator(model="meta-llama/Llama-2-7b-chat-hf")
format_enforcer = LMFormatEnforcerLocalGenerator(model, character_level_parser)
pipeline = Pipeline()
pipeline.add_component(instance=format_enforcer, name='model')


result = pipeline.run({
    "model": {"prompt": prompt}
})
print(result['model']['replies'][0])

```
The model will be inferred with the format enforcer, and the output will look like this:

```
{
"first_name": "Michael",
"last_name": "Jordan",
"year_of_birth": 1963,
"num_seasons_in_nba": 15
}
```
For a full example, see the [example notebook](https://github.com/noamgat/lm-format-enforcer/blob/main/samples/colab_haystackv2_integration.ipynb)

