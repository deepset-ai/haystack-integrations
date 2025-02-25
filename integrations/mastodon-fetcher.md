---
layout: integration
name: Mastodon Fetcher
description: A custom component to fetch a mastodon usernames latest posts
authors:
    - name: Tuana Çelik
      socials:
        github: tuanacelik
        twitter: tuanacelik
        linkedin: https://www.linkedin.com/in/tuanacelik
pypi: https://pypi.org/project/mastodon-fetcher-haystack/
repo: https://github.com/tuanacelik/mastodon-fetcher-haystack
type: Data Ingestion
report_issue: https://github.com/tuanacelik/mastodon-fetcher-haystack/issues
logo: /logos/mastodon.png
version: Haystack 2.0
toc: true
---
The `MastodonFetcher` is a simple custom component that fetches the `last_k_posts` of a given Mastodon username.
You can see a demo of this custom component in the [🦄 Should I Follow?](https://huggingface.co/spaces/deepset/should-i-follow) space on Hugging Face 🤗.

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview
This component expects `username` to be a complete Mastodon username. For example "tuana@sigmoid.social". If the provided username is correct and public, `MastodonFetcher` will return a list of `Document` objects where the contents are the users latest posts.

## Installation
```bash
pip install mastodon-fetcher-haystack
```

## Usage
You can use this component on its own, or in a pipeline.

### On its own:
```python
from mastodon_fetcher_haystack.mastodon_fetcher import MastodonFetcher

mastodon_fetcher = MastodonFetcher()
mastodon_fetcher.run(username="tuana@sigmoid.social")
```
### In a pipeline

```python
from haystack import Pipeline
from haystack.utils import Secret
from mastodon_fetcher_haystack.mastodon_fetcher import MastodonFetcher
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

mastodon_fetcher = MastodonFetcher()
prompt_builder = PromptBuilder(template='YOUR_PROMPT_TEMPLATE')
llm = OpenAIGenerator(api_key=Secret.from_token("YOUR_OPENAI_API_KEY"))

pipe = Pipeline()
pipe.add_component("fetcher", mastodon_fetcher)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)

pipe.connect("fetcher.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.prompt")
pipe.run(data={"fetcher": {"username": "tuana@sigmoid.social"}})
```

## Limitations
1. The way this component is set up is very particular with how it expects usernames. Make sure you provide the full username, e.g.: `username@instance`
2. By default, the Mastodon API allows requesting up to 40 posts.
