---
layout: integration
name: Ray
description: Run and scale Haystack Pipelines with Ray in distributed manner
authors:
  - name: Sergey Bondarenco
    socials:
      github: prosto
pypi: https://pypi.org/project/ray-haystack/
repo: https://github.com/prosto/ray-haystack
type: Distributed Computing
report_issue: https://github.com/prosto/ray-haystack/issues
logo: /logos/ray.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Start with an example](#start-with-an-example)
  - [Read pipeline events](#read-pipeline-events)
  - [Component Serialization](#component-serialization)
  - [DocumentStore with Ray](#documentstore-with-ray)
  - [RayPipeline Settings](#raypipeline-settings)
  - [Middleware](#middleware)
- [Resources](#resources)
- [License](#license)

## Overview

`ray-haystack` is a python package which allows running [Haystack pipelines](https://docs.haystack.deepset.ai/docs/pipelines) on [Ray](https://docs.ray.io/en/latest/ray-overview/index.html)
in a distributed manner. The package provides the same API to build and run Haystack pipelines, but under the hood, components are being distributed to remote nodes for execution using Ray primitives.
Specifically, [Ray Actor](https://docs.ray.io/en/latest/ray-core/actors.html) is created for each component in a pipeline to `run` its logic.

The purpose of this library is to showcase the ability to run Haystack in a distributed setup with Ray featuring its options to configure the payload, e.g:

- Control with [resources](https://docs.ray.io/en/latest/ray-core/scheduling/resources.html) how much CPU/GPU is needed for a component to run (per each component if needed)
- Manage [environment dependencies](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html) for components to run on dedicated machines.
- Run pipeline on Kubernetes using [KubeRay](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started.html)

Most of the time, you will run Haystack pipelines on your local environment; even in production, you will want to run the pipeline on a single node if the goal is to return a response quickly to the user without the overhead you would usually get with a distributed setup. However, in the case of long running and complex RAG pipelines distributed way might help:

- Not every component needs GPU, most will use some external API calls. With Ray it should be possible to assign respective resource requirements (CPU, RAM) per component execution needs.
- Some components might take longer to run, so ideally, if there is an option to parallelize component execution, it would decrease pipeline run time.
- With asynchronous execution, it should be possible to interact with different component execution stages (e.g. fire an event before and after the component starts).

`ray-haystack` provides a custom implementation for pipeline execution logic with the goal to stay **as compliant as possible with native Haystack implementation**.
In most cases, you should expect the same results (outputs) from pipeline runs. On top of that, the package will parallelize component runs where possible.
Components with no active dependencies can be scheduled without waiting for currently running components.

![Ray Pipeline Parallel](https://raw.githubusercontent.com/deepset-ai/haystack-integrations/main/images/ray-pipeline-concurrent.gif)

## Installation

`ray-haystack` can be installed as any other Python library, using pip:

```shell
pip install ray-haystack
```

The package should work with python version 3.8 and onwards. If you plan to use `ray-haystack` with an existing Ray cluster, make sure you align python and `ray` versions with those running in the cluster.

> **Note**
> The `ray-haystack` package will install both `haystack-ai` and `ray` as transitive dependencies. The minimum supported version of haystack is `2.6.0`.

If you would like to see [Ray dashboard](https://docs.ray.io/en/latest/ray-observability/getting-started.html) when starting Ray cluster locally, install Ray as follows:

```shell
pip install -U "ray[default]"
pip install ray-haystack
```

While pipeline is running locally, access the dashboard in the browser at [http://localhost:8265](http://localhost:8265).

## Usage

### Start with an example

Once `ray-haystack` is installed, let's demonstrate how it works by running a simple example.

We will build a pipeline that fetches RSS news headlines from the list of given URLs and converts each headline to a `Document` with content equal to the headline title. We then ask LLM (`OpenAIGenerator`) to create a news summary from the list of converted Documents, given a prompt `template`.

```python
import io
import os
from typing import List, Optional
from xml.etree.ElementTree import parse as parse_xml

import ray # Import ray
from haystack import Document, component
from haystack.components.builders import PromptBuilder
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.dataclasses import ByteStream

from ray_haystack import RayPipeline # Import RayPipeline (instead of `from haystack import Pipeline`)

# Please introduce your OpenAI Key here
os.environ["OPENAI_API_KEY"] = "You OpenAI Key"

@component
class XmlConverter:
    """
    Custom component which parses given RSS feed (from ByteStream) and extracts values by a
    given XPath, e.g. ".//channel/item/title" will find "title" for each RSS feed item.
    A Document is created for each extracted title. The `category` attribute can be used as
    an additional metadata field.
    """

    def __init__(self, xpath: str = ".//channel/item/title", category: Optional[str] = None):
        self.xpath = xpath
        self.category = category

    @component.output_types(documents=List[Document])
    def run(self, sources: List[ByteStream]):
        documents: List[Document] = []
        for source in sources:
            xml_content = io.StringIO(source.to_string())
            documents.extend(
                Document(content=elem.text, meta={"category": self.category})
                for elem in parse_xml(xml_content).findall(self.xpath)  # noqa: S314
                if elem.text
            )
        return {"documents": documents}

template = """
Given news headlines below provide a summary of what is happening in the world right now in a couple of sentences.
You will be given headline titles in the following format: "<headline category>: <headline title>".
When creating summary pay attention to common news headlines as those could be most insightful.

HEADLINES:
{% for document in documents %}
    {{ document.meta["category"] }}: {{ document.content }}
{% endfor %}

SUMMARY:
"""

# Create instance of Ray pipeline
pipeline = RayPipeline()

pipeline.add_component("tech-news-fetcher", LinkContentFetcher())
pipeline.add_component("business-news-fetcher", LinkContentFetcher())
pipeline.add_component("politics-news-fetcher", LinkContentFetcher())
pipeline.add_component("tech-xml-converter", XmlConverter(category="tech"))
pipeline.add_component("business-xml-converter", XmlConverter(category="business"))
pipeline.add_component("politics-xml-converter", XmlConverter(category="politics"))
pipeline.add_component("document_joiner", DocumentJoiner(sort_by_score=False))
pipeline.add_component("prompt_builder", PromptBuilder(template=template))
pipeline.add_component("generator", OpenAIGenerator())  # "gpt-4o-mini" is the default model

pipeline.connect("tech-news-fetcher", "tech-xml-converter.sources")
pipeline.connect("business-news-fetcher", "business-xml-converter.sources")
pipeline.connect("politics-news-fetcher", "politics-xml-converter.sources")
pipeline.connect("tech-xml-converter", "document_joiner")
pipeline.connect("business-xml-converter", "document_joiner")
pipeline.connect("politics-xml-converter", "document_joiner")
pipeline.connect("document_joiner", "prompt_builder")
pipeline.connect("prompt_builder", "generator.prompt")

# Draw pipeline and save it to `pipe.png`
# pipeline.draw("pipe.png")

# Start local Ray cluster
ray.init()

# Prepare pipeline inputs by specifying RSS urls for each fetcher
pipeline_inputs = {
    "tech-news-fetcher": {
        "urls": [
            "https://www.theverge.com/rss/frontpage/",
            "https://techcrunch.com/feed",
            "https://cnet.com/rss/news",
            "https://wired.com/feed/rss",
        ]
    },
    "business-news-fetcher": {
        "urls": [
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
            "https://www.business-standard.com/rss/home_page_top_stories.rss",
            "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        ]
    },
    "politics-news-fetcher": {
        "urls": [
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000113",
            "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        ]
    },
}

# Run pipeline with inputs
result = pipeline.run(pipeline_inputs)

# Print response from LLM
print("RESULT: ", result["generator"]["replies"][0])
```

Key takeways from the example:

- import `ray` module
- import `RayPipeline` (from `ray_haystack`) instead of `Pipeline` class from `haystack`
- before running the pipeline, start [local ray cluster](https://docs.ray.io/en/latest/ray-core/starting-ray.html#start-ray-init) with explicit `ray.init()` call

Under the hood, `RyaPipeline` creates actors for each component in the pipeline and runs it in a distributed manner until no components are left to run. By default, `RyaPipeline` blocks until the pipeline finishes its execution.

### Read pipeline events

In some cases, you would want to react asynchronously to particular pipeline execution points:

- when pipeline starts
- before component runs
- after component finishes
- after pipeline finishes

Internally, `RayPipeline` creates an instance of [Ray Queue](https://docs.ray.io/en/latest/ray-core/api/doc/ray.util.queue.Queue.html) where such events are stored and can be consumed.

Except for the standard `run` method, `RayPipeline` provides a method called `run_nowait`, which returns pipeline execution results without blocking current logic. We can use `run_nowait` to iterate over pipeline events, e.g.

```python
result = pipeline.run_nowait(pipeline_inputs)

for pipeline_event in result.pipeline_events_sync():
    print(
        f"\n>>> [{pipeline_event.time}] Source: {pipeline_event.source} | Type: {pipeline_event.type} | Data={pipeline_event.data}"
    )
```

### Component Serialization

If you run native Haystack pipeline locally, the components remain in the same python process, and there is no reason to care about the distributed setup. When RayPipeline runs in a distributed manner, it should be able to [serialize](https://docs.ray.io/en/latest/ray-core/objects/serialization.html) components before they end up in a remote task or actor.

The `ray-haystack` package relies on Haystack's standard `to_dict` and `from_dict` methods to serialize and deserialize components, respectively.
Please refer to the main [documentation](https://github.com/prosto/ray-haystack?tab=readme-ov-file#component-serialization) for a detailed explanation and features that handle edge cases.

### DocumentStore with Ray

When you use [InMemoryDocumentStore](https://docs.haystack.deepset.ai/docs/inmemorydocumentstore) or any DocumentStore which runs in memory with `RayPipeline`, you will stumble upon an apparent issue: in a distributed environment, these document stores running in memory will fail to operate as components that reference the store will not point to a single instance but rather a copy of it.

`ray-haystack` package provides a wrapper around `InMemoryDocumentStore` by implementing a proxy pattern so that only a single instance of `InMemoryDocumentStore` across Ray cluster is present. With that, components can share a single store. Use `RayInMemoryDocumentStore`, `RayInMemoryEmbeddingRetriever` or `RayInMemoryBM25Retriever` in case you need in-memory document store in your Ray pipelines.

### RayPipeline Settings

When an actor is created in Ray, we can control its behavior by providing certain [settings](https://docs.ray.io/en/latest/ray-core/api/doc/ray.actor.ActorClass.options.html).

`ray-haystack` provides means to configure pipeline Actors with the help of `RayPipelineSettings` dictionary:

```python
from typing import Any, Dict

from ray_haystack import RayPipeline, RayPipelineSettings

settings: RayPipelineSettings = {
    "common": {
        "actor_options": {
            "namespace": "haystack",  # common namespace name for all actors
        }
    },
    "components": {
        "per_component": {
            "generator": {
                "actor_options": {
                    "num_cpus": 2,  # component specific CPU resource requirement
                }
            }
        }
    },
}

# Option 1 - Pass settings through pipeline's metadata
pipeline = RayPipeline(metadata={"ray": settings})

pipeline_inputs: Dict[str, Any] = {}

# Option 2 - Pass settings when in the `run` method
pipeline.run(pipeline_inputs, ray_settings=settings)
```

### Middleware

Sometimes it might be useful to let custom logic run before and after component actor runs the component.

It is possible to build custom middleware:

```python
from typing import Any, Literal

import ray
from haystack.components.fetchers import LinkContentFetcher

from ray_haystack import RayPipeline, RayPipelineSettings
from ray_haystack.middleware import ComponentMiddleware, ComponentMiddlewareContext
from ray_haystack.serialization import worker_asset

ray.init()

@worker_asset
class TraceMiddleware(ComponentMiddleware):
    def __init__(self, capture: Literal["input", "output", "input_and_output"] = "input_and_output"):
        self.capture = capture

    def __call__(self, component_input, ctx: ComponentMiddlewareContext) -> Any:
        print(f"Tracer: Before running component '{ctx['component_name']}' with inputs: '{component_input}'")

        outputs = self.next(component_input, ctx)

        print(f"Tracer: After running component '{ctx['component_name']}' with outputs: '{outputs}'")

        return outputs

pipeline = RayPipeline()
pipeline.add_component("cocktail_fetcher", LinkContentFetcher())

settings: RayPipelineSettings = {
    "components": {
        "per_component": {
            # Middleware applies only to "cocktail_fetcher" component
            "cocktail_fetcher": {
                "middleware": {
                    "trace": {"type": "__main__.TraceMiddleware"},
                },
            },
        }
    },
}

response = pipeline.run(
    {
        "cocktail_fetcher": {"urls": ["https://www.thecocktaildb.com/api/json/v1/1/random.php"]},
    },
    ray_settings=settings,
)
```

## Resources

- The full documentation is available in the [repository](https://github.com/prosto/ray-haystack/tree/main)
- Explore more advanced examples:
  - [Trace Haystack Pipelines in Browser](https://github.com/prosto/ray-haystack/blob/main/examples/pipeline_watch/README.md)
  - [Running Haystack Pipeline on Kubernetes](https://github.com/prosto/ray-haystack/blob/main/examples/pipeline_kubernetes/README.md)
  - [Run pipeline with detached component actors](https://github.com/prosto/ray-haystack/tree/main/examples/pipeline_detached_actors)
- [Learn more about Ray](https://docs.ray.io/en/latest/ray-overview/getting-started.html)

## License

`ray-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
