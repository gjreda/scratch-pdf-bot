from dotenv import load_dotenv
from typing import List
import openai
import os

load_dotenv()


def embed_text(texts: List[str]) -> List[List[float]]:
    res = openai.Embedding.create(
        engine="text-embedding-ada-002",
        input=texts,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    return [record["embedding"] for record in res["data"]]
