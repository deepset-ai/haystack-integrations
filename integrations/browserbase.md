---
layout: integration
name: Browserbase
description: Use Browserbase headless browsers with Haystack
authors:
    - name: Browserbase
      socials:
        github: https://github.com/browserbase
        twitter: https://twitter.com/browserbasehq
        linkedin: https://www.linkedin.com/company/browserbasehq
pypi: https://pypi.org/project/browserbase-haystack
repo: https://github.com/browserbase/haystack
report_issue: https://github.com/browserbase/haystack/issues
type: Data Ingestion
logo: /logos/browserbase.png
version: Haystack 2.0
---

# Browserbase Haystack Fetcher

[Browserbase](https://browserbase.com) is a serverless platform for running headless browsers, it offers advanced debugging, session recordings, stealth mode, integrated proxies and captcha solving.

## Installation and setup

- Get an API key from [browserbase.com](https://browserbase.com) and set it in environment variables (`BROWSERBASE_API_KEY`).
- Install the required dependencies:

```
pip install browserbase-haystack
```

## Usage

You can load webpages into Haystack using `BrowserbaseFetcher`. Optionally, you can set `text_content` parameter to convert the pages to text-only representation.

### Standalone

```py
from browserbase_haystack import BrowserbaseFetcher

browserbase_fetcher = BrowserbaseFetcher()
browserbase_fetcher.run(urls=["https://example.com"], text_content=False)
```

### In a pipeline

```py
from browserbase_haystack import BrowserbaseFetcher
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

prompt_template = (
    "Tell me the titles of the given pages. Pages: {{ documents }}"
)
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator()

pipe = Pipeline()
pipe.add_component("fetcher", self.browserbase_fetcher)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", llm)

pipe.connect("fetcher.documents", "prompt_builder.documents")
pipe.connect("prompt_builder.prompt", "llm.prompt")
result = pipe.run(data={"fetcher": {"urls": ["https://example.com"]}})
```
