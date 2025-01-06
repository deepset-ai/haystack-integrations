---
layout: integration
name: Trafilatura
description: Efficiently gather text and metadata on the Web for LLM and RAG
authors:
    - name: Adrien Barbaresi
      socials:
        github: adbar
        twitter: adbarbaresi
        linkedin: https://www.linkedin.com/in/adrienbarbaresi
pypi: https://pypi.org/project/trafilatura/
repo: https://github.com/adbar/trafilatura
report_issue: https://github.com/adbar/trafilatura/issues
type: Data Ingestion
version: Haystack 2.0
---


### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Settings](#settings)


### Overview

Trafilatura is a cutting-edge Python package and command-line tool designed to gather text on the Web and simplify the process of turning raw HTML into structured, meaningful data. Its extraction component is seamlessly integrated into Haystack.

Going from HTML bulk to essential parts can alleviate many problems related to text quality by focusing on the actual content and avoiding the noise, which is beneficial for LLM applications.


### Installation

```bash
pip install haystack-ai trafilatura
```


### Usage

Trafilatura powers the `HTMLToDocument` class in Haystack's converters. Here is how to use it:

```python
from haystack.components.converters import HTMLToDocument

converter = HTMLToDocument()
results = converter.run(sources=["path/to/sample.html"])
documents = results["documents"]
print(documents[0].content)
# 'This is a text from the HTML file.'
```


### Settings

The `.run()` method takes an optional `extraction_kwargs` parameter which is then passed to Trafilatura. It has to be a dictionary of arguments known to the package, here are useful ideas in this context:

- Choice of HTML elements
   - `include_comments=True` (comment sections at the bottom of articles)
   - `include_images=True`
   - `include_tables=True` (active by default)
   - `prune_xpath=["//p[@class='discarded']"]` (XPath expressions to prune the tree before extraction)
- Optimization for precision or recall:
   - `favor_precision=True`: if your results contain too much noise
   - `favor_recall=True`: if parts of your documents are missing

For more information see the [Python usage](https://trafilatura.readthedocs.io/en/latest/usage-python.html) and [function description](https://trafilatura.readthedocs.io/en/latest/corefunctions.html#extract) parts of the official documentation.
