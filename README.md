# Haystack Integrations

This repository is an index of Haystack integrations that can be used with a Haystack Pipeline or Agent.

These integrations are maintained by their respective owner or authors. You can browse them on the [Haystack Integrations](https://haystack.deepset.ai/integrations) page, where you will find information on the Author(s), installation and usage of each tool.

## What are Haystack Integrations?

A Haystack Integration are Custom Nodes, DocumentStores or Agent Tools that are either external packages or additional technologies that can be used with Haystack. Some integrations may be maintained by the deepset team, others are community contributions that are owned by the authors of the integration. 

## Looking for prompts?

Prompts for the `PromptNode` and `Agent` can be found on our [Prompt Hub](https://prompthub.deepset.ai).
To contribute a prompt, follow instructions in the [`prompthub`](https://github.com/deepset-ai/prompthub) repo.

## How to contribute

To contribute, create a PR add an `.md` file to the `integrations/` directory. A few things to include in the file 👇
The frontmatter has to include the following:
```
---
name: Name of your integration (required)
description: A short description (this will appear on the front page element of your integration on the website) (required)
authors:
    - name: Name of Author 1 (required)
      socials:
        github: include if desired
        twitter: include if desired
    - name: Name of Author 2
      socials:
        github: include if desired
        twitter: include if desired
pypi: url of pypi package if exists
repo: url of GitHub repo if exists 
type: Custom Node OR Document Store OR Agent Tool (required)
report_issue: url to where people can report an issue with the integration
---
```
Note that there should be at least one of either the `pypi` or `repo` fields for us to merge the integration.

Then, please add as much information and instructions about your Integration as possible as the body of your `.md` file.

Open a Pull Request, and congrats, if all goes well, you will see your integration on the integrations page in no time 🥳
