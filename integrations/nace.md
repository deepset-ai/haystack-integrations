---
layout: integration
name: Nace
description: Route text, classify documents and evaluate RAG answers with Nace's Drex decision models in Haystack applications.
authors:
    - name: Nace AI
      socials:
        github: nace-ai
        linkedin: https://www.linkedin.com/company/nace-ai/
pypi: https://pypi.org/project/nace-haystack
repo: https://github.com/nace-ai/nace-haystack
type: Model Provider
report_issue: https://github.com/nace-ai/nace-haystack/issues
logo: /logos/nace.png
version: Haystack 3.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Nace](https://nace.ai) builds Drex, a family of decision models. Instead of generating text, a Drex model answers typed questions about a text, and about images on Drex Max, and returns calibrated probabilities:

- `choice`: picks one label from a set of options.
- `score`: rates the text on ordered levels.
- `noul`: returns the probability that a yes/no statement is true.

The `nace-haystack` package brings these models to Haystack through four components:

- `NaceTextRouter` routes a text to the output of the label the model picks for it, with an optional `low_confidence` output for uncertain answers and an optional `probabilities` output with the full answer.
- `NaceDocumentClassifier` answers typed questions about each document and stores the answers in its metadata.
- `NaceFaithfulnessEvaluator` judges whether an answer is supported by its contexts.
- `NaceContextRelevanceEvaluator` judges whether the retrieved contexts help answer the question.

The two evaluators have the same inputs and outputs as Haystack's built-in `FaithfulnessEvaluator` and `ContextRelevanceEvaluator`.

You choose a model with the `model` parameter:

- `drex-max-v1.1` (Drex Max v1.1) is the default. It reads text, JSON and images.
- `drex-v2.0` reads text only and bills fewer tokens on short texts.

Both take many questions in one request; see [Drex's limits](https://console.nace.ai/docs/drex/reference/limits).

Prices are per input token and differ by model (output is free); see [Drex pricing](https://console.nace.ai/docs/drex/reference/pricing). The default model changes when Drex releases a new one, and a new model can shift probabilities, so pin `model=` if your pipeline relies on thresholds.

To use the hosted models, you'll need an API key from the [Nace console](https://console.nace.ai). Add it as an environment variable, `NACE_API_KEY`. To use a different API host, set `api_base_url` (or `NACE_BASE_URL` before constructing the component) and pass an explicit provider key through `api_key=Secret.from_env_var("PROVIDER_API_KEY")`. Set `PROVIDER_API_KEY` to that provider's key; `NACE_API_KEY` is reserved for Nace's production API. The destination is saved with the component, so changing the environment later does not redirect an existing component. For more information, see [the Drex docs](https://console.nace.ai/docs).

Drex is also available through OpenRouter. Set `api_base_url="https://openrouter.ai/api/v1"`, set `model` to an OpenRouter model ID such as `nace-ai/drex-max`, and pass your OpenRouter key as `api_key`, for example `Secret.from_env_var("OPENROUTER_API_KEY")`.

## Installation

```bash
pip install nace-haystack
```

The package needs Python 3.11 or later and Haystack 3 (`haystack-ai>=3.0.0`).

## Usage

### Route text

`NaceTextRouter` has one output per label. With `min_confidence` set, texts whose answer is less confident than the threshold go to the `low_confidence` output instead, so you can send them to a fallback such as an LLM or a human.

```python
from haystack_integrations.components.routers.nace import NaceTextRouter

router = NaceTextRouter(
    labels={
        "billing": "Payments, invoices, refunds and charges",
        "technical": "Bugs, crashes and errors in the product",
    },
    instructions="Which team should handle this support request?",
    min_confidence=0.6,
)

result = router.run(text="I was charged twice for my subscription.")
print(result)
# One output holds the text: the label the model picked ("billing" or "technical"),
# or "low_confidence" if the answer is below min_confidence.
```

To get the full answer as well, set `include_probabilities=True`. The router then has a `probabilities` output with the picked label, its confidence and the probability of every label, so your pipeline can apply its own thresholds.

```python
from haystack_integrations.components.routers.nace import NaceTextRouter

router = NaceTextRouter(labels=["billing", "technical"], include_probabilities=True)

result = router.run(text="The app crashes every time I open the settings page.")
print(result["probabilities"])
```

### Classify documents

`NaceDocumentClassifier` sends each document to the model and stores the answers under `meta["nace"]`, keyed by question ID. Documents that can't be classified are returned in `failed_documents`, with the reason in `meta["classification_error"]`. Requests run in parallel, up to `max_workers` at a time.

All of a document's questions go in one request, which costs fewer tokens than asking them one by one. [Drex's limits](https://console.nace.ai/docs/drex/reference/limits) say how many questions a request can carry.

```python
from haystack import Document
from haystack_integrations.components.classifiers.nace import NaceDocumentClassifier

classifier = NaceDocumentClassifier(
    questions={
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this ticket?",
            "criteria": {"billing": None, "technical": None, "sales": None},
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this ticket?",
            "criteria": ["can wait", "this week", "today"],
        },
        "refund": {"type": "noul", "instructions": "Is the customer asking for a refund?"},
    },
)

result = classifier.run(documents=[Document(content="I was charged twice, please refund me today.")])

answers = result["documents"][0].meta["nace"]
print(answers["department"]["choice"], answers["department"]["confidence"])
print(answers["refund"]["noul"])
print(result["failed_documents"])
```

A `choice` answer holds the picked label, its confidence and the probability of every label. A `score` answer holds a score on the ordered levels. A `noul` answer holds the probability that the statement is true.

To send each document down a different branch of a pipeline based on its answers, connect the classifier to a `MetadataRouter`:

```python
from haystack import Document, Pipeline
from haystack.components.routers import MetadataRouter
from haystack_integrations.components.classifiers.nace import NaceDocumentClassifier

labels = ["billing", "technical"]

pipeline = Pipeline()
pipeline.add_component(
    "classifier",
    NaceDocumentClassifier(
        questions={
            "department": {
                "type": "choice",
                "instructions": "Which department should handle this ticket?",
                "criteria": dict.fromkeys(labels),
            }
        },
    ),
)
pipeline.add_component(
    "router",
    MetadataRouter(
        rules={label: {"field": "meta.nace.department.choice", "operator": "==", "value": label} for label in labels}
    ),
)
pipeline.connect("classifier.documents", "router.documents")

result = pipeline.run(
    {
        "classifier": {
            "documents": [
                Document(content="I was charged twice for my subscription."),
                Document(content="The app crashes every time I open the settings page."),
            ]
        }
    }
)
for output, documents in result["router"].items():
    print(output, [document.content for document in documents])
```

### Images on Drex Max

The default model, `drex-max-v1.1`, reads images together with the text. Pass them to `NaceTextRouter.run` as `images`: `ImageContent` or `ByteStream` objects, or files you uploaded to Drex with nace-sdk. In `instructions` and in label descriptions, refer to them as "Image 1", "Image 2" and so on. Images that are too big for one request are shrunk automatically, which needs Pillow (`pip install pillow`).

`drex-v2.0` reads text only, so passing it images raises an error. The evaluators also take an optional `images` argument, with one list of images per item.

```python
from haystack.dataclasses import ImageContent
from haystack_integrations.components.routers.nace import NaceTextRouter

router = NaceTextRouter(
    labels={
        "invoice": "Image 1 shows an invoice",
        "receipt": "Image 1 shows a receipt",
        "other": "Image 1 shows something else",
    },
    instructions="What kind of document does Image 1 show?",
)

image = ImageContent.from_file_path("attachment.png")
result = router.run(text="Please find the document attached.", images=[image])
print(result)
```

### Evaluate RAG answers

`NaceFaithfulnessEvaluator` and `NaceContextRelevanceEvaluator` take the same inputs and return the same outputs as Haystack's built-in `FaithfulnessEvaluator` and `ContextRelevanceEvaluator`, so they fit into an existing evaluation pipeline. Each item is one Drex request that returns the probability of "yes":

- `NaceFaithfulnessEvaluator` asks whether every claim in the answer is supported by the contexts.
- `NaceContextRelevanceEvaluator` asks whether the contexts contain information that helps answer the question.

Pass `instructions` to change the question. The outputs are `score` (the mean of the item scores), `individual_scores` (one probability per item), and `results` and `meta` (one entry per item).

```python
from haystack_integrations.components.evaluators.nace import (
    NaceContextRelevanceEvaluator,
    NaceFaithfulnessEvaluator,
)

questions = ["Who wrote Frankenstein?", "What is the capital of Kazakhstan?"]
contexts = [
    ["Frankenstein is a novel by Mary Shelley, first published in 1818."],
    ["Astana is the capital of Kazakhstan."],
]
# The second answer contradicts its context.
predicted_answers = ["Mary Shelley wrote Frankenstein.", "The capital of Kazakhstan is Almaty."]

faithfulness = NaceFaithfulnessEvaluator()
result = faithfulness.run(questions=questions, contexts=contexts, predicted_answers=predicted_answers)
print(result["score"], result["individual_scores"])

relevance = NaceContextRelevanceEvaluator()
result = relevance.run(questions=questions, contexts=contexts)
print(result["score"], result["individual_scores"])
```

### Switching from TypeSafe

If you use Jev through [`typesafe-haystack`](https://pypi.org/project/typesafe-haystack), made by deepset, the Nace components mirror `TypeSafeTextRouter` and `TypeSafeDocumentClassifier`: they take the same parameters and return the same outputs.

In Python code that uses the defaults, change the import, the class name and the API key environment variable (`TYPESAFE_API_KEY` becomes `NACE_API_KEY`). The default model changes from `jev-latest` to `drex-max-v1.1` with the class:

```diff
-from haystack_integrations.components.routers.typesafe import TypeSafeTextRouter
-from haystack_integrations.components.classifiers.typesafe import TypeSafeDocumentClassifier
+from haystack_integrations.components.routers.nace import NaceTextRouter
+from haystack_integrations.components.classifiers.nace import NaceDocumentClassifier

-router = TypeSafeTextRouter(labels=["billing", "technical"], min_confidence=0.6)
+router = NaceTextRouter(labels=["billing", "technical"], min_confidence=0.6)

-classifier = TypeSafeDocumentClassifier(questions=questions)
+classifier = NaceDocumentClassifier(questions=questions)
```

If your code sets `model` explicitly, change it to `drex-max-v1.1` too. Nace does not translate Jev model IDs, so `jev-latest` has to be replaced.

The classifier stores answers under `meta["nace"]` instead of `meta["typesafe"]`. If your code reads the old key, for example in a `MetadataRouter` rule, use the new key or pass `metadata_field="typesafe"` to keep the old one.

In a saved YAML pipeline, change the `type:` paths, `TYPESAFE_API_KEY` to `NACE_API_KEY`, and `model: jev-latest` to `model: drex-max-v1.1`. The destination is saved with the component, so also replace an explicit `api_base_url: https://api.typesafe.ai` with `https://console.nace.ai`; otherwise the component still targets TypeSafe and fails Nace's credential guard. TypeSafe writes `api_base_url` into every saved component, as `null` by default; if it is `null`, there is nothing to change.

```diff
 components:
   classifier:
     init_parameters:
       api_key:
         env_vars:
-        - TYPESAFE_API_KEY
+        - NACE_API_KEY
         strict: true
         type: env_var
       ...
-      api_base_url: https://api.typesafe.ai
+      api_base_url: https://console.nace.ai
-      model: jev-latest
+      model: drex-max-v1.1
       ...
-    type: haystack_integrations.components.classifiers.typesafe.document_classifier.TypeSafeDocumentClassifier
+    type: haystack_integrations.components.classifiers.nace.document_classifier.NaceDocumentClassifier
```

A saved pipeline already contains `metadata_field: typesafe`, so its classifier keeps writing answers under `meta["typesafe"]`. A `TypeSafeTextRouter` entry needs the same edits, including `api_base_url` when it is set.

`NaceTextRouter` adds image input and the `probabilities` output, and the package adds the two evaluators. The package has no counterpart to `TypeSafeRanker`.

### License

`nace-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
