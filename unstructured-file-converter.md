---
layout: integration
name: Unstructured File Converter
description: Component to easily convert files and directories into Documents using the Unstructured API
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/unstructured-fileconverter-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/components/converters/unstructured_fileconverter
type: Custom Node
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/unstructured.svg
version: Haystack 2.0
---

Component for the Haystack (2.x) LLM framework to easily convert files and directories into Documents using the Unstructured API.

**[Unstructured](https://unstructured-io.github.io/unstructured/index.html)** provides a series of tools to do **ETL for LLMs**. This component calls the Unstructured API that simply extracts text and other information from a vast range of file formats.
**[Supported file types](https://unstructured-io.github.io/unstructured/api.html#supported-file-types)**.

## Installation

```bash
pip install unstructured-fileconverter-haystack
```

### Hosted API
If you plan to use the hosted version of the Unstructured API, you just need the **(free) Unsctructured API key**. You can get it by signing up [here](https://unstructured.io/api-key).

### Local API (Docker)
If you want to run your own local instance of the Unstructured API, you need Docker and you can find instructions [here](https://unstructured-io.github.io/unstructured/api.html#using-docker-images).

In short, this should work:
```bash
docker run -p 8000:8000 -d --rm --name unstructured-api quay.io/unstructured-io/unstructured-api:latest --port 8000 --host 0.0.0.0
```

## Usage

### In isolation
```python
import os
from unstructured_fileconverter_haystack import UnstructuredFileConverter

os.environ["UNSTRUCTURED_API_KEY"] = "YOUR-API-KEY"

converter = UnstructuredFileConverter()

documents = converter.run(paths = ["a/file/path.pdf", "a/directory/path"])["documents"]
    
```

### In a Haystack Pipeline
```python
import os
from haystack.preview import Pipeline
from haystack.preview.components.writers import DocumentWriter
from haystack.preview.document_stores import InMemoryDocumentStore
from unstructured_fileconverter_haystack import UnstructuredFileConverter

os.environ["UNSTRUCTURED_API_KEY"] = "YOUR-API-KEY"

document_store = InMemoryDocumentStore()

indexing = Pipeline()
indexing.add_component("converter", UnstructuredFileConverter())
indexing.add_component("writer", DocumentWriter(document_store))
indexing.connect("converter", "writer")

indexing.run({"converter": {"paths": ["a/file/path.pdf", "a/directory/path"]}})
```

## Configuration

### Initialization parameters
- `api_url`: URL of the Unstructured API. Defaults to the hosted version. If you run the API locally, you should specify this parameter.
- `api_key`: API key for the Unstructured API (https://unstructured.io/api-key).
                        If you run the API locally, it is not needed.
                        If you use the hosted version, it defaults to the environment variable UNSTRUCTURED_API_KEY.
- `document_creation_mode`: How to create Haystack Documents from the elements returned by Unstructured.
  - `"one-doc-per-file"`: One Haystack Document per file. All elements are concatenated into one text field.
  - `"one-doc-per-page"`: One Haystack Document per page. All elements on a page are concatenated into one text field.
  - `"one-doc-per-element"`: One Haystack Document per element. Each element is converted to a Haystack Document
  - `separator`: Separator between elements when concatenating them into one text field.
- `unstructured_kwargs`: Additional keyword arguments that are passed to the Unstructured API. They can be helpful to improve or speed up the conversion. See https://unstructured-io.github.io/unstructured/api.html#parameters.
-  `progress_bar`: Show a progress bar for the conversion. Defaults to True.