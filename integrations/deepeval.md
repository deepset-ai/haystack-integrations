---
layout: integration
name: DeepEval
description: Use the DeepEval evaluation framework to calculate model-based metrics 
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/deepeval-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/deepeval
type: Evaluation Framework
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/deepeval.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [DeepEvalEvaluator](#DeepEvalEvaluator)

## Overview

[DeepEval](https://github.com/confident-ai/deepeval) (by [Confident AI](https://www.confident-ai.com/)) is an open source framework for model-based evaluation to evaluate your LLM applications by quantifying their performance on aspects such as faithfulness, answer relevancy, contextual recall etc. More information can be found on the [documentation page](https://docs.haystack.deepset.ai/docs/deepevalevaluator).

## Installation

Install the DeepEval integration:
```bash
pip install deepeval-haystack
```

## Usage

Once installed, you will have access to a [DeepEvalEvaluator](https://docs.haystack.deepset.ai/docs/deepevalevaluator) that supports a variety of model-based evaluation metrics: 
- Answer Relevancy
- Faithfulness
- Contextual Precision
- Contextual Recall
- Contextual Relevance

In addition to evaluation scores, DeepEval's evaluators offer additional reasoning for each evaluation.

### DeepEvalEvaluator

To use this integration for calculating model-based evaluation metrics, initialize a `DeepEvalEvaluator` with the metric name and metric input parameters: 

```python
from haystack import Pipeline
from haystack_integrations.components.evaluators.deepeval import DeepEvalEvaluator, DeepEvalMetric

QUESTIONS = [
    "Which is the most popular global sport?",
    "Who created the Python language?",
]
CONTEXTS = [
    [
        "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact.",
        "Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people.",
    ],
    [
        "Python, created by Guido van Rossum in the late 1980s, is a high-level general-purpose programming language.",
        "Its design philosophy emphasizes code readability, and its language constructs aim to help programmers write clear, logical code for both small and large-scale software projects.",
    ],
]
RESPONSES = [
    "Football is the most popular sport with around 4 billion followers worldwide",
    "Python language was created by Guido van Rossum.",
]

pipeline = Pipeline()
evaluator = DeepEvalEvaluator(
    metric=DeepEvalMetric.FAITHFULNESS,
    metric_params={"model": "gpt-4"},
)
pipeline.add_component("evaluator", evaluator)

# Each metric expects a specific set of parameters as input. Refer to the
# DeepEvalMetric class' documentation for more details.
results = pipeline.run({"evaluator": {"questions": QUESTIONS, "contexts": CONTEXTS, "responses": RESPONSES}})

for output in results["evaluator"]["results"]:
    print(output)
```
