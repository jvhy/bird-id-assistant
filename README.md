# Bird ID Assistant 🦆

## Goals

The overall goal of this project is to create a bird identification assistant based on Retrieval Augmented Generation (RAG). The two main components are:

1. A vector database containing embeddings of documents with information about bird species
2. A Large Language Model assistant with access to said database which, when prompted with a description of a bird, retrieves the closest matching species document and provides an answer to the user

Some personal learning goals include:

1. Learning more about data collection via web scraping
2. Researching Python tools for converting HMTL / free text to a vector database
3. Familiarizing myself with different frameworks for RAG and learning how LLMs retrieve documents from an embedding space
4. Learning more about birds! :-)


## Instructions

### Requirements

- Python 3.13 installed
- Ollama installed (see instructions [here](https://ollama.com/download/linux))

### Installation

0. Clone this repository
```
$ git@github.com:jvhy/bird-id-assistant.git
```

1. Install the package

```
# Via Makefile recipe:
$ make install
$ source venv/bin/activate


# Or manually:
$ python3.13 -m venv --clear venv
$ source venv/bin/activate
$ python3 -m pip install .
```

### Data scraping

1. Scrape a dataset of bird species articles from Wikipedia:


```
# Via Makefile recipe:
$ make dataset


# Or via CLI:
$ mkdir dataset
$ bia collect dataset
```

2. Start Chroma vector database:

```
$ chroma run --path chroma --log-path chroma.log
```

3. Insert scraped articles into the database:

```
# Via Makefile recipe:
$ make insert


# Or via CLI:
$ bia db create dataset/
```

### Run assistant

0. Ensure that Chroma is running (see step 2 of the previous section)

1. (In a new terminal) Start ollama:
```
ollama serve
```

2. (In a new terminal) Pull the model from Ollama registry:
```
$ ollama pull llama3.1:8b-instruct-q4_K_M
```

3. Start assistant:
```
$ bia run
>  # start prompting...
```
