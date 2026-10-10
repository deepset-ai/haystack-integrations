---
layout: integration
name: TypeSafe
description: Classify documents and route text with TypeSafe's System One decision models, such as Jev, in Haystack applications.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/typesafe-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/typesafe
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/typesafe.png
version: Haystack 2.0
toc: true
enterprise: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[TypeSafe](https://typesafe.ai) builds System One models, such as Jev, which make fast, structured decisions for software. Instead of generating text, a System One model answers typed questions about a text in a single request and returns calibrated probabilities:

- `choice`: picks one label from a set of options.
- `score`: rates the text on ordered levels.
- `noul`: returns the probability that a yes/no question is true.

The `typesafe-haystack` package brings these models to Haystack through two components:

- `TypeSafeDocumentClassifier` answers typed questions about each document and stores the answers in its metadata.
- `TypeSafeTextRouter` routes a text to the output of the label the model picks for it, with an optional `low_confidence` output for uncertain answers.

Both components also work with servers that implement the TypeSafe API, such as [Ollaya](https://ollaya.dev), which runs open decision models on your own machine.

To use TypeSafe's hosted models, you'll need an API key from the [TypeSafe console](https://console.typesafe.ai). Add it as an environment variable, `TYPESAFE_API_KEY`. For more information, see [the TypeSafe docs](https://docs.typesafe.ai).

## Installation

```bash
pip install typesafe-haystack
```

## Usage

### Classify documents

`TypeSafeDocumentClassifier` sends each document to the model and stores the answers under `meta["typesafe"]`, keyed by question ID. Documents that can't be classified are returned in `failed_documents`.

```python
from haystack import Document
from haystack_integrations.components.classifiers.typesafe import TypeSafeDocumentClassifier

classifier = TypeSafeDocumentClassifier(
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
print(result["documents"][0].meta["typesafe"])
# {'department': {'type': 'choice', 'choice': 'billing', 'confidence': 0.9516,
#                 'probabilities': {'billing': 0.9677, 'technical': 0.0221, 'sales': 0.0102}},
#  'urgency': {'type': 'score', 'score': 1.948, 'confidence': 0.9389,
#              'legend': {'0': 'can wait', '1': 'this week', '2': 'today'},
#              'probabilities': {'0': 0.0113, '1': 0.0295, '2': 0.9593}},
#  'refund': {'type': 'noul', 'noul': 0.9498}}
```

To send each document down a different branch of a pipeline based on its answers, connect the classifier to a `MetadataRouter`:

```python
from haystack import Document, Pipeline
from haystack.components.routers import MetadataRouter
from haystack_integrations.components.classifiers.typesafe import TypeSafeDocumentClassifier

labels = ["billing", "technical"]

pipeline = Pipeline()
pipeline.add_component(
    "classifier",
    TypeSafeDocumentClassifier(
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
        rules={
            label: {"field": "meta.typesafe.department.choice", "operator": "==", "value": label}
            for label in labels
        }
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
print({output: [document.content for document in documents] for output, documents in result["router"].items()})
# {'billing': ['I was charged twice for my subscription.'],
#  'technical': ['The app crashes every time I open the settings page.'],
#  'unmatched': []}
```

### Route text

`TypeSafeTextRouter` has one output per label. With `min_confidence` set, texts whose answer is less confident than the threshold go to the `low_confidence` output instead, so you can send them to a fallback such as an LLM or a human.

```python
from haystack_integrations.components.routers.typesafe import TypeSafeTextRouter

router = TypeSafeTextRouter(
    labels={
        "billing": "Payments, invoices, refunds and charges",
        "technical": "Bugs, crashes and errors in the product",
    },
    instructions="Which team should handle this support request?",
    min_confidence=0.6,
)

print(router.run(text="I was charged twice for my subscription."))
# {'billing': 'I was charged twice for my subscription.'}
```

### Run open models locally with Ollaya

[Ollaya](https://ollaya.dev) serves open decision models through the TypeSafe API. Start it and pull a model:

```bash
docker run -d --name ollaya -p 11435:11435 -v ollaya:/home/ollaya/.ollaya ghcr.io/ollaya-dev/ollaya
docker exec ollaya ollaya pull laya:en
```

Then point either component at the server with `api_base_url` and pick one of its models. Ollaya accepts any non-empty API key unless it is configured with one:

```python
from haystack.utils import Secret
from haystack_integrations.components.routers.typesafe import TypeSafeTextRouter

router = TypeSafeTextRouter(
    labels=["billing", "technical"],
    model="laya:en",
    api_key=Secret.from_token("local"),
    api_base_url="http://localhost:11435",
)

print(router.run(text="The app crashes every time I open the settings page."))
# {'technical': 'The app crashes every time I open the settings page.'}
```

### License

`typesafe-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
