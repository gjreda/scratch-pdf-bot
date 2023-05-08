# GPT PDF Chatbot

This is a prototype of a chatbot that can answer questions about PDFs. It uses [OpenAI's API](https://openai.com/blog/openai-api/) for language modeling, and [LanceDB](https://lancedb.github.io/lancedb/) for vector storage and retrieval.

## Setup
This uses [Poetry](https://python-poetry.org/) for dependency management. To install dependencies:
```
$ poetry install
```

You'll also need to create a `.env` file and add your `OPENAI_API_KEY` to it (see `.env.example`).

## Usage

The command below will run the pipeline on the `papers` directory, which contains a few PDFs. It will then start a REPL where you can ask questions about the PDFs. You can exit the Q&A loop by typing "exit" or cmd/ctrl + c.
```
$ poetry run python main.py --pdf_directory=papers
```

## Example
[/static/example.png](/static/example.png)