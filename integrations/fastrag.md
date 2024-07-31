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
type: Custom Component
report_issue: https://github.com/IntelLabs/fastRAG/issues
logo: /logos/intel-labs.png
version: Haystack 2.0
toc: true
---

fast**RAG** is a research framework for ***efficient*** and ***optimized*** retrieval augmented generative pipelines,
incorporating state-of-the-art LLMs and Information Retrieval. fastRAG is designed to empower researchers and developers
with a comprehensive tool-set for advancing retrieval augmented generation.

Comments, suggestions, issues and pull-requests are welcomed! ❤️

> **IMPORTANT**
> 
> Now compatible with Haystack v2+. Please report any possible issues you find.

## 📣 Updates

- **2024-05**: fastRAG V3 is Haystack 2.0 compatible 🔥
- **2023-12**: Gaudi2 and ONNX runtime support; Optimized Embedding models; Multi-modality and Chat demos; [REPLUG](https://arxiv.org/abs/2301.12652) text generation.
- **2023-06**: ColBERT index modification: adding/removing documents.
- **2023-05**: [RAG with LLM and dynamic prompt synthesis example](https://github.com/IntelLabs/fastRAG/blob/main/examples/rag-prompt-hf.ipynb).
- **2023-04**: Qdrant `DocumentStore` support.

## Key Features

- **Optimized RAG**: Build RAG pipelines with SOTA efficient components for greater compute efficiency.
- **Optimized for Intel Hardware**: Leverage [Intel extensions for PyTorch (IPEX)](https://github.com/intel/intel-extension-for-pytorch), [🤗 Optimum Intel](https://github.com/huggingface/optimum-intel) and [🤗 Optimum-Habana](https://github.com/huggingface/optimum-habana) for *running as optimal as possible* on Intel® Xeon® Processors and Intel® Gaudi® AI accelerators.
- **Customizable**: fastRAG is built using [Haystack](https://github.com/deepset-ai/haystack) and HuggingFace. All of fastRAG's components are 100% Haystack compatible.

## 🚀 Components

For a brief overview of the various unique components in fastRAG refer to the [Components Overview](https://github.com/IntelLabs/fastRAG/blob/main/components.md) page.

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
    <td><a href="https://github.com/IntelLabs/fastRAG/blob/main/components.md#fastrag-running-quantized-llms-using-openvino">OpenVINO</a></td>
    <td><em>Running quantized LLMs using OpenVINO</td>
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

## 📍 Installation

Preliminary requirements:

- **Python** 3.8 or higher.
- **PyTorch** 2.0 or higher.

To set up the software, clone the project and run the following, preferably in a newly created virtual environment:

```bash
pip install fastrag
```

There are [additional dependencies](https://github.com/IntelLabs/fastRAG?tab=readme-ov-file#extra-packages) that you can install based on your specific usage of fastRAG.

For the example below, we need to install extra packages via the following command:

```bash
pip install fastrag[intel, openvino]
```

## Usage

You can import components from fastRAG and use them in a Haystack pipeline:

```python
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.rankers import TransformersSimilarityRanker

from fastrag.generators.openvino import OpenVINOGenerator

prompt_template = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{query}}
Answer:
"""

openvino_compressed_model_path = "path/to/quantized/model"

generator = OpenVINOGenerator(
    model="microsoft/phi-2",
    compressed_model_dir=openvino_compressed_model_path,
    device_openvino="CPU",
    task="text-generation",
    generation_kwargs={
        "max_new_tokens": 100,
    }
)

pipe = Pipeline()

pipe.add_component("retriever", InMemoryBM25Retriever(document_store=store))
pipe.add_component("ranker", TransformersSimilarityRanker())
pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipe.add_component("llm", generator)

pipe.connect("retriever.documents", "ranker.documents")
pipe.connect("ranker", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "Who is the main villan in Lord of the Rings?"
answer_result = pipe.run({
    "prompt_builder": {
        "query": query
    },
    "retriever": {
        "query": query
    },
    "ranker": {
        "query": query,
        "top_k": 1
    }
})

print(answer_result["llm"]["replies"][0])
#' Sauron\n'
```

For more examples, check out [Example Use Cases](https://github.com/IntelLabs/fastRAG/blob/main/examples.md). 

## License

The code is licensed under the [Apache 2.0 License](https://github.com/IntelLabs/fastRAG/blob/main/LICENSE).

## Disclaimer

This is not an official Intel product.
