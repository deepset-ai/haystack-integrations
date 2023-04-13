---
layout: integration
name: Fact Checking rocks!
description: Fact checking baseline combining dense retrieval and textual entailment.
authors:
    - name: Stefano Fiorucci
      socials:
        github: anakin87
pypi:
repo: https://github.com/anakin87/fact-checking-rocks
type: Custom Node
report_issue: https://github.com/anakin87/fact-checking-rocks/issues
---
## Idea

**Fact Checking rocks** 🎸 is a simple webapp that demonstrates how a baseline for fact checking can be built by combining dense retrieval and a textual entailment task. In a nutshell, the flow is as follows:

- the user enters a factual statement
- the relevant passages are retrieved from the knowledge base using dense retrieval
- the system computes the text entailment between each relevant passage and the statement, using a Natural Language Inference model
- the entailment scores are aggregated to produce a summary score.
- Bonus step: the final decision is explained using a Large Language Model 

## The EntailmentChecker: a custom Haystack node
This project is strongly based on 🔎 Haystack and incudes a custom Haystack node (the `EntailmentChecker`), that checks the entailment between every document content and the query
and returns aggregate entailment information.

## Installation

💻 To install this project locally, follow these steps:
* `git clone https://github.com/anakin87/fact-checking-rocks`
* `cd fact-checking-rocks`
* `pip install -r requirements.txt`

To run the web app, simply type: `streamlit run Rock_fact_checker.py`
