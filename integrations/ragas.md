---
layout: integration
name: Ragas
description: Use the Ragas evaluation framework to calculate model-based metrics 
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: deepset-ai
pypi: https://pypi.org/project/ragas-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ragas
type: Evaluation Framework
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/ragas.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [RagasEvaluator](#RagasEvaluator)

## Overview

[Ragas](https://docs.ragas.io/) is an open source framework for model-based evaluation to evaluate your LLM applications by quantifying their performance on aspects such as correctness, tonality, hallucination, fluency, etc. More information can be found on the [documentation page](https://docs.haystack.deepset.ai/v2.0/docs/ragasevaluator).

## Installation

Install the Ragas integration:
```bash
pip install ragas-haystack
```

## Usage

Once installed, you will have access to a [RagasEvaluator](https://docs.haystack.deepset.ai/v2.0/docs/ragasevaluator) that supports a variety of model-based evaluation metrics: 
- Faithfulness
- Answer relevancy
- Context recall
- Context precision
- Context relevancy
- Aspect Critique

### RagasEvaluator

To use this integration for calculating model-based evaluation metrics, initialize a `RagasEvaluator` with the metric name and optional metric input parameters: 

```python
# A valid OpenAI API key must be provided as an environment variable "OPENAI_API_KEY" to run this example.

from haystack import Pipeline

from haystack_integrations.components.evaluators.ragas import RagasEvaluator, RagasMetric

QUESTIONS = [
    "Which is the most popular global sport?",
    "Who created the Python language?",
]
CONTEXTS = [
    [
        "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people."
    ],
    [
        "Python, created by Guido van Rossum in the late 1980s, is a high-level general-purpose programming language. Its design philosophy emphasizes code readability, and its language constructs aim to help programmers write clear, logical code for both small and large-scale software projects."
    ],
]
RESPONSES = [
    "Football is the most popular sport with around 4 billion followers worldwide",
    "Python language was created by Guido van Rossum.",
]

GROUND_TRUTHS = [
    "Football is the most popular sport",
    "Python language was created by Guido van Rossum.",
]

pipeline = Pipeline()
evaluator_context = RagasEvaluator(
    metric=RagasMetric.CONTEXT_PRECISION,
)
evaluator_aspect = RagasEvaluator(
    metric=RagasMetric.ASPECT_CRITIQUE,
    metric_params={"name": "custom", "definition": "Is this answer problematic for children?", "strictness": 3},
)
pipeline.add_component("evaluator_context", evaluator_context)
pipeline.add_component("evaluator_aspect", evaluator_aspect)

# Each metric expects a specific set of parameters as input. Refer to the
# Ragas class' documentation for more details.
results = pipeline.run(
    {
        "evaluator_context": {"questions": QUESTIONS, "contexts": CONTEXTS, "ground_truths": GROUND_TRUTHS},
        "evaluator_aspect": {"questions": QUESTIONS, "contexts": CONTEXTS, "responses": RESPONSES},
    }
)

for component in ["evaluator_context", "evaluator_aspect"]:
    for output in results[component]["results"]:
        print(output)
```
