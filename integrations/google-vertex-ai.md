---
layout: integration
name: Google Vertex AI
description: Use Google Vertex AI Models with Haystack
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/google-vertex-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/google_vertex
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/vertexai.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [Gemini API models](#gemini-api-models)
    - [PaLM API models](#palm-api-models)
    - [Codey API models](#codey-api-models)
    - [Imagen API models](#imagen-api-models)

## Overview

[Vertex AI](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview) is a machine learning (ML) platform that lets you train and deploy ML models and AI applications, and customize large language models (LLMs) for use in your AI-powered applications. This integration enables the usage of [models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models) through Vertex AI API on Google Cloud Platform (GCP). 

Haystack supports [Gemini API models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#gemini-models), [PaLM API models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#palm-models), [Codey APIs models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#codey-models), and [Imagen API models](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#imagen-models) for task such as **text generation**, **function calling**, **image generation**, **visual question answering**, **code generation**, and **image captioning**.

> To learn more about the use cases and test Vertex AI models with Haystack, follow this [Colab Notebook](https://colab.research.google.com/drive/1hOLxbLHsyGsOd6E9qjA-CnZSH-eoLxp8?usp=sharing).

> There is an article about Gemini models and how to use them with Haystack: [Gemini Models with Google Vertex AI Integration for Haystack](https://haystack.deepset.ai/blog/gemini-models-with-google-vertex-for-haystack)

## Installation

Install the Google Vertex AI integration:
```bash
pip install google-vertex-haystack
```

## Usage

Once installed, you will have access to various Haystack Generators: 
- [`GeminiGenerator`](https://docs.haystack.deepset.ai/v2.0/docs/geminigenerator): Use this component with Gemini models '**gemini-pro**' and '**gemini-pro-vision**' for text generation and multimodal prompts.
- [`GeminiChatGenerator`](https://docs.haystack.deepset.ai/v2.0/docs/geminichatgenerator): Use this component with Gemini models '**gemini-pro**' and '**gemini-pro-vision**' for text generation, multimodal prompts and function calling in chat completion setting.
- `VertexAITextGenerator`: Use this component with PaLM models for text generation.
- `VertexAICodeGenerator`: Use this component with Codey model for code generation and code completion.
- `VertexAIImageGenerator`: Use this component with Imagen model '**imagegeneration**' for image generation.
- [`VertexAIImageCaptioner`](https://docs.haystack.deepset.ai/v2.0/docs/vertexaiimagecaptioner): Use this component with Imagen model '**imagetext**' for image captioning.
- `VertexAIImageQA`: Use this component with Imagen model '**imagetext**' for visual question answering.

To use Vertex AI models, you need to have a Google Cloud Platform account and be logged in using Application Default Credentials (ADCs). For more info see the [official documentation](https://colab.research.google.com/corgiredirector?site=https%3A%2F%2Fcloud.google.com%2Fdocs%2Fauthentication%2Fprovide-credentials-adc). 

To start using Vertex AI generators in Haystack, you need to set the `project_id` variable to a valid project ID that have enough authorization to use Vertex AI. Find your `project_id` in the [GCP resource manager](https://console.cloud.google.com/cloud-resource-manager) or locally by running `gcloud projects list` in your terminal. For more info on the gcloud CLI see the [official documentation](https://cloud.google.com/cli).

### Gemini API models

You can leverage Gemini models through two components: [GeminiGenerator](https://docs.haystack.deepset.ai/v2.0/docs/coheregenerator) and [GeminiChatGenerator](https://docs.haystack.deepset.ai/v2.0/docs/geminichatgenerator). You can use these components on their own or in a pipeline.  

**Text Generation with `gemini-pro`** 

To use Gemini model for text generation, initialize a `GeminiGenerator` with `"gemini-pro"` and `project_id`: 

```python
from google_vertex_haystack.generators.gemini import GeminiGenerator

gemini_generator = GeminiGenerator(model="gemini-pro", project_id=project_id)
result = gemini_generator.run(parts = ["What is assemblage in art?"])
print(result["answers"][0])
```
Output: 
```shell
Assemblage in art refers to the creation of a three-dimensional artwork by combining various found objects...
```

**Multimodality with `gemini-pro-vision`** 

To use `gemini-pro-vision` model for visual question answering, initialize a `GeminiGenerator` with `"gemini-pro-vision"` and `project_id`. Then, run it with the images as well as the prompt:

```python
import requests
from haystack.dataclasses.byte_stream import ByteStream

URLS = [
    "https://raw.githubusercontent.com/silvanocerza/robots/main/robot1.jpg",
    "https://raw.githubusercontent.com/silvanocerza/robots/main/robot2.jpg",
    "https://raw.githubusercontent.com/silvanocerza/robots/main/robot3.jpg",
    "https://raw.githubusercontent.com/silvanocerza/robots/main/robot4.jpg"
]
images = [
    ByteStream(data=requests.get(url).content, mime_type="image/jpeg")
    for url in URLS
]
gemini_generator = GeminiGenerator(model="gemini-pro-vision", project_id=project_id)
result = gemini_generator.run(parts = ["What can you tell me about these robots?", *images])
for answer in result["answers"]:
    print(answer)  
```
Output:
```shell
The first image is of C-3PO and R2-D2 from the Star Wars franchise...
The second image is of Maria from the 1927 film Metropolis...
The third image is of Gort from the 1951 film The Day the Earth Stood Still...
The fourth image is of Marvin from the 1977 film The Hitchhiker's Guide to the Galaxy...
```

*For function calling with `gemini-pro`, refer to the [Colab Notebook](https://colab.research.google.com/drive/1hOLxbLHsyGsOd6E9qjA-CnZSH-eoLxp8?usp=sharing).*

### PaLM API Models

You can leverage PaLM API models `text-bison`, `text-unicorn` and `text-bison-32k` through `VertexAITextGenerator` for task generation. To use PaLM models, initialize a `VertexAITextGenerator` with model name and `project_id`.

Here'a an example of using `text-unicorn` model with VertexAITextGenerator to extract information as a JSON file:

```python
from google_vertex_haystack.generators.text_generator import VertexAITextGenerator

palm_llm = VertexAITextGenerator(model="text-unicorn", project_id=project_id)
palm_llm_result = palm_llm.run(
    """Extract the technical specifications from the text below in a JSON format. Valid fields are name, network, ram, processor, storage, and color.
       Text: Google Pixel 7, 5G network, 8GB RAM, Tensor G2 processor, 128GB of storage, Lemongrass
       JSON:
    """)
print(palm_llm_result["answers"][0])
```

### Codey API Models

You can leverage Codey API models, `code-bison`, `code-bison-32k` and `code-gecko`, through `VertexAICodeGenerator` for code generation. To use Codey models, initialize a `VertexAICodeGenerator` with model name and `project_id`.

Here'a an example of using `code-bison` model for **code generation**:
```python
from google_vertex_haystack.generators.code_generator import VertexAICodeGenerator

codey_llm = VertexAICodeGenerator(model="code-bison", project_id=project_id)
codey_llm_result = codey_llm.run("Write a code for calculating fibonacci numbers in JavaScript")
print(codey_llm_result["answers"][0])
```

Here'a an example of using `code-gecko` model for **code completion**:
```python
from google_vertex_haystack.generators.code_generator import VertexAICodeGenerator

codey_llm = VertexAICodeGenerator(model="code-gecko", project_id=project_id)
codey_llm_result = codey_llm.run("""function fibonacci(n) {
  // Base cases
  if (n <= 1) {
    return n;
  }
""")
print(codey_llm_result["answers"][0])
```

### Imagen API models

You can leverage Imagen models through three components: [VertexAIImageCaptioner](https://colab.research.google.com/corgiredirector?site=https%3A%2F%2Fdocs.haystack.deepset.ai%2Fv2.0%2Fdocs%2Fvertexaiimagecaptioner), `VertexAIImageGenerator` and `VertexAIImageQA`.

**Image Generation with `imagegeneration`**

To generate an image, initialize a VertexAIImageGenerator with the `imagegeneration` and the `project_id`, Then, you can run it with a prompt:

```python
import io
import PIL.Image as Image
from google_vertex_haystack.generators.image_generator import VertexAIImageGenerator

image_generator = VertexAIImageGenerator(model="imagegeneration", project_id=project_id)
image_generator_result = image_generator.run("magazine style, 4k, photorealistic, modern red armchair, natural lighting")

## (Optional) Save the generated image
image = Image.open(io.BytesIO(image_generator_result["images"][0].data))
image.save("output.png")
```

**Image Captioning with `imagetext`** 

To use generate image captions, initialize a VertexAIImageCaptioner with the `imagetext` model and `project_id`. Then, you can run the VertexAIImageCaptioner with the image that you want to caption: 

```python
from google_vertex_haystack.generators.captioner import VertexAIImageCaptioner

image_captioner = VertexAIImageCaptioner(model='imagetext', project_id=project_id)
image = ByteStream.from_file_path("output.png") # you can use the generated image

image_captioner_result = image_captioner.run(image=image)
print(image_captioner_result["captions"])
```

**Visual Question Answering (VQA) with `imagetext`** 

To answers questions about an image, initialize a VertexAIImageQA with the `imagetext` model and `project_id`. Then, you can run it with the `image` and the `question`: 

```python
from haystack.dataclasses.byte_stream import ByteStream
from google_vertex_haystack.generators.question_answering import VertexAIImageQA

visual_qa = VertexAIImageQA(model='imagetext', project_id=project_id)
image = ByteStream.from_file_path("output.png") # you can use the generated image
question = "what's the color of the furniture?"

visual_qa_result = visual_qa.run(image=image,question=question) 
print(visual_qa_result["answers"])
```