---
layout: integration
name: Notion Extractor
description: A component to extract pages from Notion to Haystack Documents. Useful for indexing Pipelines.
authors:
    - name: Bogdan Kostić
      socials:
        github: bogdankostic
pypi: https://pypi.org/project/notion-haystack/
repo: https://github.com/bogdankostic/notion-haystack
type: Custom Node
report_issue: https://github.com/bogdankostic/notion-haystack/issues
logo: /logos/notion.png
---
This Haystack component allows you to easily export your Notion pages to Haystack Documents by providing a Notion API token.

Given that the Notion API is subject to some [rate limits](https://developers.notion.com/reference/request-limits),
this component will automatically retry failed requests and wait for the rate limit to reset before retrying. This is
especially useful when exporting a large number of pages. Furthermore, this component uses `asyncio` to make requests in
parallel, which can significantly speed up the export process.

## Installation

```bash
pip install notion-haystack
```

## Usage

To use this component, you will need a Notion API token. You can follow the steps outlined in the [Notion documentation](https://developers.notion.com/docs/create-a-notion-integration#create-your-integration-in-notion) 
to create a new Notion integration, connect it to your pages, and obtain your API token.

The following minimal example demonstrates how to export a list of pages to Haystack Documents:
```python
from notion_haystack import NotionExporter

exporter = NotionExporter(api_token="<your-token>")
exported_pages = exporter.run(file_paths=["<list-of-page-ids>"])

# exported_pages will be a list of Haystack Documents where each Document corresponds to a Notion page
```

The following example shows how to use the `NotionExporter` inside an indexing pipeline:
```python
from notion_haystack import NotionExporter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Pipeline

document_store = InMemoryDocumentStore()
exporter = NotionExporter(api_token="<your-token>")

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=exporter, name="exporter", inputs=["File"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=["exporter"])
indexing_pipeline.run(file_paths=["<list-of-page-ids>"])

# The pages will now be indexed in the document store
```

The `NotionExporter` class takes the following arguments:
- `api_token`: Your Notion API token. You can find information on how to get an API token in [Notion's documentation](https://developers.notion.com/docs/create-a-notion-integration)
- `export_child_pages`: Whether to recursively export all child pages of the provided page ids. Defaults to `False`.
- `extract_page_metadata`: Whether to extract metadata from the page and add it as a frontmatter to the markdown. 
                           Extracted metadata includes title, author, path, URL, last editor, and last editing time of 
                           the page. Defaults to `False`.
- `exclude_title_containing`: If specified, pages with titles containing this string will be excluded. This might be
                              useful for example to exclude pages that are archived. Defaults to `None`.

The `NotionExporter.run` method takes the following arguments:
- `file_paths`: A list of page ids to export. If `export_child_pages` is `True`, all child pages of these pages will be
                exported as well.
