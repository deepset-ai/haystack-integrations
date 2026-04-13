---
layout: integration
name: Superlinked
description: Use Superlinked (SIE) embeddings, reranking, and extraction in Haystack RAG pipelines.
authors:
    - name: Superlinked
      socials:
        github: superlinked
        linkedin: superlinked
pypi: https://pypi.org/project/sie-haystack/
repo: https://github.com/superlinked/sie/tree/main/integrations/sie_haystack
type: Model Provider
report_issue: https://github.com/superlinked/sie/issues
logo: /logos/superlinked.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Components](#components)
- [Resources](#resources)
- [License](#license)

## Overview

[Superlinked](https://superlinked.com) is a self-hosted inference engine (SIE) for embedding, reranking, and extraction. The `sie-haystack` package provides Haystack 2.0 components for 85+ embedding models (dense, sparse, multivector/ColBERT, and multimodal), cross-encoder reranking, and zero-shot entity/relation/classification extraction, all powered by a single SIE endpoint.

For the full integration guide with code examples, parameters, and supported models, see the [Superlinked Haystack docs](https://superlinked.com/docs/integrations/haystack/).

## Installation

```bash
pip install sie-haystack
```

This installs `sie-sdk` and `haystack-ai` as dependencies. You also need a running SIE instance; see the [Superlinked Haystack docs](https://superlinked.com/docs/integrations/haystack/#start-the-server) for how to start the SIE server.

## Components

`sie-haystack` exposes Haystack-native components for every SIE capability. All components share the same `base_url` / `model` configuration and run against a single SIE endpoint. Follow each link for the full reference in the Superlinked Haystack docs.

- **[Embedders](https://superlinked.com/docs/integrations/haystack/#embedders)**: `SIETextEmbedder`, `SIEDocumentEmbedder` (dense embeddings for queries and documents, with optional `meta_fields_to_embed` support)
- **[Sparse Embeddings](https://superlinked.com/docs/integrations/haystack/#sparse-embeddings)**: `SIESparseTextEmbedder`, `SIESparseDocumentEmbedder` (learned sparse vectors from SPLADE or BGE-M3 for hybrid search)
- **[Multivector (ColBERT) Embeddings](https://superlinked.com/docs/integrations/haystack/#multivector-colbert-embeddings)**: `SIEMultivectorTextEmbedder`, `SIEMultivectorDocumentEmbedder` (per-token embeddings for late-interaction models)
- **[Image Embeddings](https://superlinked.com/docs/integrations/haystack/#image-embeddings)**: `SIEImageEmbedder` (CLIP, SigLIP, ColPali for multimodal pipelines)
- **[Reranking](https://superlinked.com/docs/integrations/haystack/#reranking)**: `SIERanker` (cross-encoder and ColBERT / late-interaction rerankers, swappable by model name)
- **[Extraction](https://superlinked.com/docs/integrations/haystack/#extraction)**: `SIEExtractor` (zero-shot entities via GLiNER, relations via GLiREL, classifications via GLiClass, object detection via GroundingDINO / OWL-v2)

See the [Configuration Options](https://superlinked.com/docs/integrations/haystack/#configuration-options) section of the Superlinked Haystack docs for the full parameter reference for every component.

## Resources

- [Superlinked Haystack integration guide](https://superlinked.com/docs/integrations/haystack/)
- [`sie-haystack` source](https://github.com/superlinked/sie/tree/main/integrations/sie_haystack)
- [`sie-haystack` on PyPI](https://pypi.org/project/sie-haystack/)
- [Superlinked model catalog](https://superlinked.com/models)

## License

`sie-haystack` is released under the Apache 2.0 License.
