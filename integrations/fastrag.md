---
layout: integration
name: fastRAG
description: fastRAG is a research framework for efficient and optimized retrieval augmented generative pipelines
authors:
    - name: Intel Labs
      socials:
        github: IntelLabs
pypi:
repo: https://github.com/IntelLabs/fastRAG
type: Custom Node
report_issue: https://github.com/IntelLabs/fastRAG/issues
logo: /logos/intel-labs.png
---

fast**RAG** is a research framework for ***efficient*** and ***optimized*** retrieval augmented generative pipelines,
incorporating state-of-the-art LLMs and Information Retrieval. fastRAG is designed to empower researchers and developers
with a comprehensive tool-set for advancing retrieval augmented generation.

## Key Features

- **Optimized RAG**: Build RAG pipelines with SOTA efficient components for greater compute efficiency.
- **Optimized for Intel Hardware**: Leverage [Intel extensions for PyTorch (IPEX)](https://github.com/intel/intel-extension-for-pytorch), [🤗 Optimum Intel](https://github.com/huggingface/optimum-intel) and [🤗 Optimum-Habana](https://github.com/huggingface/optimum-habana) for *running as optimal as possible* on Intel® Xeon® Processors and Intel® Gaudi® AI accelerators.
- **Customizable**: fastRAG is built using [Haystack](https://github.com/deepset-ai/haystack) and HuggingFace. All of fastRAG's components are 100% Haystack compatible.

## :rocket: Components

For a brief overview of the various unique components in fastRAG refer to the [Components Overview]([components.md](https://github.com/IntelLabs/fastRAG/blob/main/components.md)) page.

<div class="tg-wrap" align="center">
<table style="undefined;table-layout: fixed; width: 600px; text-align: center;">
<colgroup>
<!-- <col style="width: 229px"> -->
<!-- <col style="width: 238px"> -->
</colgroup>
<tbody>
  <tr>
    <td colspan="2"><strong><em>LLM Backends</em></td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#fastrag-running-llms-with-habana-gaudi-(dl1)-and-gaudi-2">Intel Gaudi Accelerators</a></td>
    <td><em>Running LLMs on Gaudi 2</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#fastrag-running-llms-with-onnx-runtime">ONNX Runtime</a></td>
    <td><em>Running LLMs with optimized ONNX-runtime</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#fastrag-running-rag-pipelines-with-llms-on-a-llama-cpp-backend">Llama-CPP</a></td>
    <td><em>Running RAG Pipelines with LLMs on a Llama CPP backend</td>
  </tr>
  <tr>
    <td colspan="2"><strong><em>Optimized Components</em></td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/scripts/optimizations/embedders/README.md">Embedders</a></td>
    <td>Optimized int8 bi-encoders</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/scripts/optimizations/reranker_quantization/quantization.md">Rankers</a></td>
    <td>Optimized/sparse cross-encoders</td>
  </tr>
  <tr>
    <td colspan="2"><strong><em>RAG-efficient Components</em></td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#ColBERT-v2-with-PLAID-Engine">ColBERT</a></td>
    <td>Token-based late interaction</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#Fusion-In-Decoder">Fusion-in-Decoder (FiD)</a></td>
    <td>Generative multi-document encoder-decoder</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#REPLUG">REPLUG</a></td>
    <td>Improved multi-document decoder</td>
  </tr>
  <tr>
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#ColBERT-v2-with-PLAID-Engine">PLAID</a></td>
    <td>Incredibly efficient indexing engine</td>
  </tr>
</tbody>
</table></div>

## :round_pushpin: Installation

Preliminary requirements:

- **Python** 3.8 or higher.
- **PyTorch** 2.0 or higher.

To set up the software, clone the project and run the following, preferably in a newly created virtual environment:



```bash
git clone https://github.com/IntelLabs/fastRAG.git
cd fastrag
pip install .
```

There are several dependencies to consider, depending on your specific usage:

```bash
# Additional engines/components
pip install .[intel]               # Intel optimized backend [Optimum-intel, IPEX]
pip install .[elastic]             # Support for ElasticSearch store
pip install .[qdrant]              # Support for Qdrant store
pip install libs/colbert           # Indexing engine for ColBERT/PLAID
pip install .[faiss-cpu]           # CPU-based Faiss library
pip install .[faiss-gpu]           # GPU-based Faiss library
pip install .[knowledge_graph]     # Libraries for working with spacy and KG

# User interface (for demos)
pip install .[ui]

# Benchmarking
pip install .[benchmark]

# Development tools
pip install .[dev]
```
