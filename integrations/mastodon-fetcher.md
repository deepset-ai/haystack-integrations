---
layout: integration
name: Mastodon Fetcher
description: A custom component to fetch a mastodon usernames latest posts
authors:
    - name: Tuana Çelik
      socials:
        github: tuanacelik
        twitter: tuanacelik
        linkedin: tuanacelik
pypi: https://pypi.org/project/mastodon-fetcher-haystack/
repo: https://github.com/tuanacelik/mastodon-fetcher-haystack
type: Custom Node
report_issue: https://github.com/tuanacelik/mastodon-fetcher-haystack/issues
logo: /logos/mastodon.png
version: Haystack 2.0
toc: true
---
The `MastodonFetcher` is a simple custom component that fetches the `last_k_posts` of a given Mastodon username.
You can see a demo of this custom component in the [🦄 Should I Follow?](https://huggingface.co/spaces/deepset/should-i-follow) space on Hugging Face 🤗.

The latest versions of `mastodon-fetcher-haystack` are compatible only with Haystack 2.x. You need to specify the version explicitly to import the `MastodonFetcher` component suitable with Haystack 1.x.

### **Table of Contents**

- [Haystack 2.0](#haystack-20)
  - [Installation (2.0)](#installation-20)
  - [Usage (2.0)](#usage-20)
- [Haystack 1.x](#haystack-1x)
  - [Installation (1.x)](#installation-1x)
  - [Usage (1.x)](#usage-1x)

## Haystack 2.0
This component expects `username` to be a complete Mastodon username. For example "tuana@sigmoid.social". If the provided username is correct and public, `MastodonFetcher` will return a list of `Document` objects where the contents are the users latest posts.

### Installation (2.0)
```bash
pip install mastodon-fetcher-haystack
```

### Usage (2.0)
You can use this component on its own, or in a pipeline.

#### On its own:
```python
from mastodon_fetcher_haystack.mastodon_fetcher import MastodonFetcher

mastodon_fetcher = MastodonFetcher()
mastodon_fetcher.run(username="tuana@sigmoid.social")
```
#### In a pipeline

```python
from haystack import Pipeline
from mastodon_fetcher_haystack.mastodon_fetcher import MastodonFetcher
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

prompt_builder = PromptBuilder(template='YOUR_PROMPT_TEMPLATE')
llm = OpenAIGenerator(api_key'YOUR_OPENAI_API_KEY')

pipe = Pipeline()
pipe.add_component("fetcher", mastodon_fetcher)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)

pipe.connect("fetcher.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.prompt")
pipe.run(data={"fetcher": {"username": "tuana@sigmoid.social"}})
```

## Haystack 1.x  

This component expects `query` to be a complete Mastodon username. For example "tuana@sigmoid.social". If the provided username is correct and public, `MastodonFetcher` will return a list of `Document` objects where the contents are the users latest posts.

### Installation (1.x)

```bash
pip install mastodon-fetcher-haystack==0.0.1
```

### Usage (1.x)

Because the component returns a list of Documents, it can be used at the same step that a Retriever would normally be used. For example, use it in a Retrieval Augmented Generative (RAG) pipeline as follows:

```python
from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from haystack.utils import print_answers
from mastodon_fetcher_haystack.mastodon_fetcher import MastodonFetcher

mastodon_fetcher = MastodonFetcher()

prompt_template = PromptTemplate(prompt="Given the follwing Mastodon posts stream, create a short summary of the topics the account posts about. Mastodon posts stream: {join(documents)};\n Answer:", 
                                output_parser=AnswerParser())
prompt_node = PromptNode(default_prompt_template=prompt_template, model_name_or_path="text-davinci-003", api_key=YOUR_OPENAI_API_KEY)

pipe = Pipeline()
pipe.add_node(component=mastodon_fetcher, name="MastodonFetcher", inputs=["Query"])
pipe.add_node(component=prompt_node, name="PromptNode", inputs=["MastodonFetcher"])
result = pipe.run(query="tuana@sigmoid.social", params={"MastodonFetcher": {"last_k_posts": 3}})
```

## Limitations
1. The way this component is set up is very particular with how it expects usernames. Make sure you provide the full username, e.g.: `username@instance`
2. By default, the Mastodon API allows requesting up to 40 posts.
