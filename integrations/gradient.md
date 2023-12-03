---
layout: integration
name: gradient
description: Gradient AI is a self-managed cloud service for Large Language Models, offering fine-tuning and inference of open-source models and embeddings generation.
authors:
  - name: Mateusz Haligowski <mhaligowski@gmail.com>
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: deepset-ai
pypi: https://pypi.org/project/gradient-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/gradient
type: Embedder, Generator
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/gradient.png
version: Haystack 2.0
---
# Gradient AI integration

[![PyPI - Version](https://img.shields.io/pypi/v/gradient-haystack.svg)](https://pypi.org/project/gradient-haystack)

-----

**Table of Contents**

- [Gradient AI integration](#gradient-ai-integration)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [License](#license)

## Installation
Use `pip` to install the integration:

```console
pip install gradient-haystack
```
## Usage
Once installed, you will have access to a Generator and two Embedder objects. To use
the Embedder to index documents:

```python
import os

from haystack import Pipeline
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter

from gradient_haystack.embedders.gradient_document_embedder import GradientDocumentEmbedder

os.environ["GRADIENT_ACCESS_TOKEN"] = "Your Gradient Access Token"
os.environ["GRADIENT_WORKSPACE_ID"] = "Your Gradient Workspace id: "

documents = [
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome."),
]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=GradientDocumentEmbedder(), name="document_embedder")
indexing_pipeline.add_component(instance=DocumentWriter(document_store=InMemoryDocumentStore()), name="document_writer")
indexing_pipeline.connect("document_embedder", "document_writer")
indexing_pipeline.run({"document_embedder": {"documents": documents}})
```

## Examples
You can find a full code example showing how to use the integration in [this Colab](https://colab.research.google.com/drive/1kE_NAKKgZztQJMbgm2esyTVkAxlrpGtd#scrollTo=coE-fMtTJ-Pp).

## License

`gradient-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
