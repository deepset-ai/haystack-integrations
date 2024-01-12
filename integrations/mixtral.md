- Explain that it's a guide on how to use OpenAIGenerator to make use of Mistral

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

api_key = "MISTRAL-API-KEY"
model = "mistral-medium"

client = OpenAIChatGenerator(
    api_key=api_key, model_name=model, api_base_url="https://api.mistral.ai/v1"
)

response = client.run(
    messages=[ChatMessage.from_user("What is the best French cheese?")]
)
print(response)
```

```python
from haystack.components.embedders import OpenAITextEmbedder

api_key = "MISTRAL-API-KEY"
model = "mistral-embed"

embedder = OpenAITextEmbedder(api_key=api_key, model_name=model, api_base_url="https://api.mistral.ai/v1")

response = embedder.run(text="What is the best French cheese?")
print(response)
# {'embedding': [-0.0186004638671875, ...],
# 'meta': {'model': 'mistral-embed', 
#'usage': {'prompt_tokens': 9, 'total_tokens': 9, 'completion_tokens': 0}}}
```