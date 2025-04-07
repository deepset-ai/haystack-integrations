# Haystack Integrations

This repository is an index of Haystack integrations that can be used with a Haystack Pipeline or Agent.

These integrations are maintained by their respective owner or authors. You can browse them on the [Haystack Integrations](https://haystack.deepset.ai/integrations) page, where you will find information on the Author(s), installation and usage of each tool.

## What are Haystack Integrations?

Haystack Integrations are a Document Store, Model Provider, Custom Component, Monitoring Tool or Evaluation Framework that are either external packages or additional technologies that can be used with Haystack. Some integrations may be maintained by the deepset team, others are community contributions owned by the authors of the integration. Read more about Haystack Integrations in [Introduction to Integrations](https://docs.haystack.deepset.ai/docs/integrations).

## How to contribute
To contribute, create a PR add an `.md` file to the `integrations/` directory.
👉 You can start off with the [draft integration page](https://github.com/deepset-ai/haystack-integrations/blob/main/draft-integration.md)
A few things to include in the file 👇
The frontmatter has to include the following:
```
---
layout: integration (required)
name: Name of your integration (required)
description: A short description (this will appear on the front page element of your integration on the website) (required)
authors:
    - name: Name of Author 1 (required)
      socials:
        github: include if desired
        twitter: include if desired
        linkedin: include if desired (full url)
    - name: Name of Author 2
      socials:
        github: include if desired
        twitter: include if desired
        linkedin: include if desired (full url)
pypi: url of pypi package if exists
repo: url of GitHub repo if exists
report_issue: url to where people can report an issue with the integration 
type: Document Store OR Model Provider OR Data Ingestion OR Monitoring Tool OR Evaluation Framework OR Custom Component OR Tool Integration OR something new! (required)
toc: true (optional)
logo: /logos/your-logo.png (optional)
version: Haystack 2.0
---
```
Note that there should be at least one of either the `pypi` or `repo` fields for us to merge the integration.

Then, please add as much information and instructions about your Integration as possible as the body of your `.md` file.

Open a Pull Request, and congrats, if all goes well, you will see your integration on the integrations page in no time 🥳
