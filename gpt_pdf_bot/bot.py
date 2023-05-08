from dotenv import load_dotenv
from typing import List
import lancedb
import openai
import os

from gpt_pdf_bot.shared import embed_text


load_dotenv()


class ChatBot:

    def __init__(self, table_name: str):
        self.db = lancedb.connect(uri='.lancedb')
        self.table = self.db[table_name]

    def run(self):
        while True:
            query = input("\nAsk me a question: ")

            if query == 'exit':
                break

            print(f"Searching for {query}", end='\n\n')
            context = self.retrieve_context(query=query)
            print(f"Found {len(context)} results", end='\n\n')

            texts = self.retrieve_text_from_context(context=context)
            annotations = self.create_annotations_from_context(context=context)

            prompt = self.generate_prompt(query=query, context=texts)

            response = self.ask_gpt(prompt, annotations=annotations)
            print(response, end='\n\n')

    def retrieve_context(self, query: str, limit: int = 5) -> List[str]:
        emb = embed_text([query])[0]

        # TODO: return and pass metadata so we can display the source and page number
        context = self.table.search(emb).limit(limit).to_df()
        return context

    def retrieve_text_from_context(self, context: List[str]) -> List[str]:
        """Extracts only the text from the context, so it can be used in the prompt"""
        # curly braces will mess up prompt templating, so remove them
        texts = context['text'].str.replace('{', '').str.replace('}', '').tolist()
        return texts

    def create_annotations_from_context(self, context: List[str]) -> List[str]:
        """Extracts the document metadata from the context,
        so it can be displayed with the LLM's response"""
        metadata = context['metadata'].tolist()

        annotations = []
        for meta in metadata:
            source = meta['source']
            page_num = meta['page_num']
            annotations.append(f"- file name: {source}, page number: {page_num}")
        return annotations


    def generate_prompt(self, query: str, context: List[str]) -> str:
        limit = 3750  # GPT-3.5's token limit is 4096
        # TODO: this is a naive implementation that doesn't handle the case where the context is too long
        prepared_context = "\n\n---\n\n".join(context)
        prompt_tmpl = f"""Answer the question based on the context below.
            {context}

            Question: {query}
            Answer:"""
        return prompt_tmpl.format(query=query, context=prepared_context)

    def ask_gpt(self, prompt: str, annotations: List[str]) -> str:
        res = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            temperature=0,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            api_key=os.environ['OPENAI_API_KEY'],
        )
        response = res['choices'][0]['text'].strip()
        annotations = '\n'.join(annotations).strip()

        answer = f"""
        Answer: {response}
        
        Here are the sources I used:
        {annotations}
        """
        return answer
