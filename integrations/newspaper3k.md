---
layout: integration
name: Newspaper3k Wrapper Nodes
description: Newspaper3k wrapper nodes. It allows to scrape articles directly using the scraper Node or crawling many pages using the crawler Node.

authors:
    - name: Haradai
      socials:
        github: haradai
pypi: https://pypi.org/project/newspaper3k-haystack
repo: https://github.com/Haradai/newspaper3k-haystack
type: Data Ingestion
report_issue: https://github.com/Haradai/newspaper3k-haystack/issues
---

Newspaper3k Haystack is a simple wrapper for the newspaper3k library within the Haystack framework. It allows to scrape articles given urls using the scraper node or crawl many pages using the crawler node.

## Installation:
You can install Newspaper3k Haystack using pip:
```
pip install newspaper3k-haystack
```

## Usage:
### Scraper Node:
```
from newspaper3k-haystack import newspaper3k_scraper
scraper = newspaper3k_scraper()

```
You can also provide a header for the request and a timeout for the page loading.
```
scraper = newspaper3k_scraper(
    headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'},
    request_timeout= 10)
```

To run in standalone mode you can use the run or run_batch if you want to load one url or multiple urls in an array.

**Available parameters:**
```
:param query: list of strings containing the webpages to scrape.
:param lang: (None by default) language to process the article with, if None autodetected.
    Available languages are: (more info at https://newspaper.readthedocs.io/en/latest/)
    input code      full name

    ar              Arabic
    ru              Russian
    nl              Dutch
    de              German
    en              English
    es              Spanish
    fr              French
    he              Hebrew
...
:param summary: (False by default) Whether to summarize the document (through nespaper3k) and save it as document metadata.
:param path: (None by default) Path where to store the downloaded articles html, if None, not downloaded. Ignored if load=True
:param load: (False by default) If true query should be a local path to an html file to scrape.
```
**In Standalone:**
```
scraper.run(query="https://www.lonelyplanet.com/articles/getting-around-norway",
    metadata=True,
    summary=True,
    keywords=True,
    path="articles")
```
**In a Pipeline:**
```

from qdrant_haystack.document_stores import QdrantDocumentStore
from haystack.nodes import EntityExtractor
from haystack.pipelines import Pipeline
from haystack.nodes import PreProcessor

document_store = QdrantDocumentStore(
    ":memory:",
    index="Document",
    embedding_dim=768,
    recreate_index=True,
)

entity_extractor = EntityExtractor(model_name_or_path="dslim/bert-base-NER",flatten_entities_in_meta_data=True)

processor = PreProcessor(
    clean_empty_lines=False,
    clean_whitespace=False,
    clean_header_footer=False,
    split_by="sentence",
    split_length=30,
    split_respect_sentence_boundary=False,
    split_overlap=0
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=scraper, name="scraper", inputs=['File'])
indexing_pipeline.add_node(component=processor, name="processor", inputs=['scraper'])
indexing_pipeline.add_node(entity_extractor, "EntityExtractor", ["processor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=['EntityExtractor'])

#we can pass the previously seen arguments also
indexing_pipeline.run(query = "https://www.roughguides.com/norway/",
    params={
        "scraper":{
            "metadata":True,
            "summary":True,
            "keywords":True
        }
    })
```
### Crawler Node:
```
from newspaper3k-haystack import newspaper3k_crawler
```
When initializing the crawler you can pass the same parameters as to the scraper node.

```
crawler = newspaper3k_crawler(
    headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'},
    request_timeout= 10)
```

**Available parameters:**
```
        :param query: list of initial urls to start scraping
        :param n_articles: number of articles to scrape per initial url
        :param beam: number of articles from each scraped website to prioritize in the crawl queue.
            If 0 then priority of scrape will be a simple continuous pile of found links after each scrape. (BFS). 
            If 1 then would be performing (DFS).
        :param filters: dictionary with lists of strings that the urls should contain or not. Keys: positive and negative.
            Urls will be checked to contain at least one positive filter and none of the negatives.
            e.g.
            {positive: [".com",".es"],
            negative: ["facebook","instagram"]}
        :param keep_links: (False by default) Whether to keep the found links in each page as document metadata or not

        :param lang: (None by default) language to process the article with, if None autodetected.
            Available languages are: (more info at https://newspaper.readthedocs.io/en/latest/)
            input code      full name

            ar              Arabic
            ru              Russian
            nl              Dutch
            de              German
            en              English
            es              Spanish
            fr              French
            he              Hebrew
            it              Italian
            ko              Korean
            no              Norwegian
            fa              Persian
            pl              Polish
            pt              Portuguese
            sv              Swedish
            hu              Hungarian
            fi              Finnish
            da              Danish
            zh              Chinese
            id              Indonesian
            vi              Vietnamese
            sw              Swahili
            tr              Turkish
            el              Greek
            uk              Ukrainian
            bg              Bulgarian
            hr              Croatian
            ro              Romanian
            sl              Slovenian
            sr              Serbian
            et              Estonian
            ja              Japanese
            be              Belarusian

        :param metadata: (False by default) Whether to get article metadata.
        :param keywords: (False by default) Whether to save the detected article keywords as document metadata.
        :param summary: (False by default) Whether to summarize the document (through nespaper3k) and save it as document metadata.
        :param path: (None by default) Path where to store the downloaded articles html, if None, not downloaded.
```
**In Standalone:** 

You can also use run_batch and pass a list of urls in the query argument. It will scrape n_articles for each provided url.
```
docs = crawler.run(
    query = "https://www.roughguides.com/norway/ ",
    n_articles = 10,
    beam = 5,
    filters = {
        "positive":["norway"],
        "negative":["facebook","instagram"]
    },
    keep_links = False,
    metadata=True,
    summary=True,
    keywords=True,
    path = "articles")
```

**In a Pipeline:**
```
from qdrant_haystack.document_stores import QdrantDocumentStore
from haystack.nodes import EntityExtractor
from haystack.pipelines import Pipeline
from haystack.nodes import PreProcessor

document_store = QdrantDocumentStore(
    ":memory:",
    index="Document",
    embedding_dim=768,
    recreate_index=True,
)

entity_extractor = EntityExtractor(model_name_or_path="dslim/bert-base-NER",flatten_entities_in_meta_data=True)

processor = PreProcessor(
    clean_empty_lines=False,
    clean_whitespace=False,
    clean_header_footer=False,
    split_by="sentence",
    split_length=30,
    split_respect_sentence_boundary=False,
    split_overlap=0
)

indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=crawler, name="crawler", inputs=['File'])
indexing_pipeline.add_node(component=processor, name="processor", inputs=['crawler'])
indexing_pipeline.add_node(entity_extractor, "EntityExtractor", ["processor"])
indexing_pipeline.add_node(component=document_store, name="document_store", inputs=['EntityExtractor'])

#we can pass the previously seen arguments also
indexing_pipeline.run(query = "https://www.roughguides.com/norway/",
    params={
        "crawler":{
            "n_articles" : 500,
            "beam" : 5,
            "filters" : {
                "positive":["norway"],
                "negative": ["facebook"]
            },
            "keep_links" : False,
            "metadata":True,
            "summary":True,
            "keywords":True,
            "path": "articles"
        }
    })
```