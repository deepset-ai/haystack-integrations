---
layout: integration
name: Mastodon Fetcher
description: A custom component to fetch a mastodon usernames latest posts
authors:
    - name: Tuana Celik
      socials:
        github: tuanacelik
        twitter: tuanacelik
pypi: https://pypi.org/project/mastodon-fetcher-haystack/
repo: https://github.com/tuanacelik/mastodon-fetcher-haystack
type: Custom Node
report_issue: https://github.com/tuanacelik/mastodon-fetcher-haystack/issues
---

The `MastodonFetcher` is a simple custom component that fetches the `last_k_posts` of a given Mastodon username.

This component expects `query` to be a complete Mastodon username. For example "tuana@sigmoid.social". If the provided username is correct and public, `MastodonFetcher` will return a list of `Document` objects where the contents are the users latest posts.

## Installation

Run `pip install mastodon-fetcher-haystack` to install the latest available release.

## Usage

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
