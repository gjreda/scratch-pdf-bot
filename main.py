from argparse import ArgumentParser
from pathlib import Path

from gpt_pdf_bot.bot import ChatBot
from gpt_pdf_bot.ingest import PdfIngestionPipeline


def main(pdf_directory: str):
    pipeline = PdfIngestionPipeline(pdf_directory=pdf_directory)
    pipeline.run()

    bot = ChatBot(table_name=pdf_directory)
    bot.run()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--pdf_directory', help='Path to directory containing PDFs to ingest')
    args = parser.parse_args()

    path = Path(args.pdf_directory)
    if not path.exists():
        raise ValueError(f"Directory {path} does not exist")

    main(pdf_directory=path.name)
