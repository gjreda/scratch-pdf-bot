from dotenv import load_dotenv
from pathlib import Path
from typing import List
import lancedb
import pypdf

from gpt_pdf_bot.shared import embed_text
from gpt_pdf_bot.types import Chunk, Document, Page

load_dotenv()


class PdfIngestionPipeline:
    def __init__(self, pdf_directory: str):
        self.pdf_directory = Path(pdf_directory)
        self.db = lancedb.connect(uri=".lancedb")

    def run(self) -> None:
        print(f"Running ingestion pipeline on {self.pdf_directory}", end="\n\n")
        documents = self.read_pdfs()
        print(f"Read {len(documents)} documents", end="\n\n")

        print("Splitting documents into chunks", end="\n\n")
        chunks = self.chunk_documents(documents=documents)

        print("Creating and persisting embeddings", end="\n\n")
        table = self.create_and_persist_embeddings(chunks=chunks)

    def read_pdfs(self) -> List[Document]:
        documents = []

        for pdf in self.pdf_directory.glob("*.pdf"):
            print(f"Reading {pdf.name}")
            reader = pypdf.PdfReader(pdf)
            doc = Document(
                source=pdf.name,
                metadata=reader.metadata,
            )

            for i, page in enumerate(reader.pages):
                doc.pages.append(
                    Page(
                        page_num=i,
                        text=page.extract_text(),
                    )
                )

            documents.append(doc)
        return documents

    def chunk_documents(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[Chunk]:
        # TODO: This is a naive implementation that is not smart about splitting on word boundaries
        chunks = []

        for doc in documents:
            for page in doc.pages:
                for i in range(0, len(page.text), chunk_size - chunk_overlap):
                    chunks.append(
                        Chunk(
                            text=page.text[i : i + chunk_size],
                            metadata={"source": doc.source, "page_num": page.page_num},
                        )
                    )
        return chunks

    def create_and_persist_embeddings(self, chunks: List[Chunk]):
        # check if table exists
        # TODO: this is a naive way to not recompute embeddings for the same pdfs
        if self.pdf_directory.name in self.db.table_names():
            print(f"Table '{self.pdf_directory.name}' already exists")
            return self.db[self.pdf_directory.name]

        texts = [chunk.text for chunk in chunks]
        embeddings = embed_text(texts=texts)

        merged = []
        for chunk, emb in zip(chunks, embeddings):
            merged.append(
                {
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "vector": emb,
                }
            )

        table = self.db.create_table(self.pdf_directory.name, data=merged)
        print(f"Wrote {len(embeddings)} embeddings to {table.name} table")
        return table
