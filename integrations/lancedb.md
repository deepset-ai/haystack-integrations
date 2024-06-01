---
layout: integration
name: LanceDB Haystack
description: A DocumentStore backed by LanceDB
authors:
    - name: Alan Meeson
      socials:
        github: alanmeeson
pypi: https://pypi.org/project/lancedb-haystack/
repo: https://github.com/alanmeeson/lancedb-haystack
type: Document Store
report_issue: https://github.com/alanmeeson/lancedb-haystack/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
LanceDB-Haystack is an embedded [LanceDB](https://lancedb.github.io/lancedb/) backed Document Store for [Haystack 2.X](https://github.com/deepset-ai/haystack/).

## Installation

The current simplest way to get LanceDB-Haystack is to install from GitHub via pip:

```pip install lancedb-haystack```

## Usage

```python
import pyarrow as pa
from lancedb_haystack import LanceDBDocumentStore
from lancedb_haystack import LanceDBEmbeddingRetriever, LanceDBFTSRetriever

# Declare the metadata fields schema, this lets us filter using it.
# See: https://arrow.apache.org/docs/python/api/datatypes.html
metadata_schema = pa.struct([
  ('title', pa.string()),    
  ('publication_date', pa.timestamp('s')),
  ('page_number', pa.int32()),
  ('topics', pa.list_(pa.string()))
])

# Create the DocumentStore
document_store = LanceDBDocumentStore(
  database='my_database', 
  table_name="documents", 
  metadata_schema=metadata_schema, 
  embedding_dims=384
)

# Create an embedding retriever
embedding_retriever = LanceDBEmbeddingRetriever(document_store)

# Create a Full Text Search retriever
fts_retriever = LanceDBFTSRetriever(document_store)
```

See also [`examples/pipeline-usage.ipynb`](https://github.com/alanmeeson/lancedb-haystack/blob/main/examples/pipeline-usage.ipynb) for a full worked example.

### License

[Apache License 2.0](https://github.com/alanmeeson/lancedb-haystack/blob/main/LICENSE)
