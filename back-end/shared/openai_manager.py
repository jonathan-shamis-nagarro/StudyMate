from enum import Enum
import os
import time
from typing import Any
import fastapi
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI,AzureOpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document

from langchain_community.callbacks import  get_openai_callback


from models.completion_response import CompletionResponse


class AzureOpenAIManager:
    def __init__(
        self
    ):
        self.api_base =  os.getenv("AZURE_OPENAI_API_URL")
        self.api_key =  os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version =  os.getenv("AZURE_OPENAI_API_VERSION")
        self.embeddings_engine =  os.getenv("AZURE_OPENAI_EMBEDDINGS_ENGINE")
        self.embeddings_model =  os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL")
        self.chat_engine =  os.getenv("AZURE_OPENAI_CHAT_ENGINE")
        self.chat_model =  os.getenv("AZURE_OPENAI_CHAT_MODEL")
        
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint = self.api_base,
            openai_api_key = self.api_key,
            openai_api_version = self.api_version,
            azure_deployment = self.embeddings_engine,
            model = self.embeddings_model,
            max_retries = 3
        )
        self.llm = AzureChatOpenAI(
            azure_endpoint = self.api_base,
            openai_api_key = self.api_key,
            openai_api_version = self.api_version,
            deployment_name = self.chat_engine,
            model = self.chat_model,
            temperature = 0,
            max_tokens = 500,
            max_retries = 3
        )
    
    def get_completion_response(self, propmt: list) -> CompletionResponse:
        try:
            with get_openai_callback() as cb:
                result = self.llm.invoke(propmt)
                return CompletionResponse(
                        message = result.content,
                        prompt_tokens = cb.prompt_tokens,
                        completion_tokens = cb.completion_tokens,
                        total_cost = cb.total_cost
                    )
                
        except Exception as e:
            raise fastapi.HTTPException(
                status_code=500, detail=f"Call to Azure OpenAI failed. Exception: {e}"
            )

    def get_embeddings(self, text: str) -> list[float]:
        try:
            
            response = self.embeddings.embed_documents([text])

            return response[0]

        except Exception as e:
            raise fastapi.HTTPException(
                status_code=500,
                detail=f"Call to Azure OpenAI failed. Exception: {e}",
            )
        

    def get_summary(self, chunks: any) -> list[float]:
        try:
            docs = []
            for chunk in chunks:
                docs.append(
                    Document(
                        page_content= chunk
                    )
                )
                

            prompt_template = """Write a concise summary of the following:
            {text}
            CONCISE SUMMARY:"""
            prompt = PromptTemplate.from_template(prompt_template)
            
            
            refine_template = (
                "Your job is to produce a final summary\n"
                "We have provided an existing summary up to a certain point: {existing_answer}\n"
                "We have the opportunity to refine the existing summary"
                "(only if needed) with some more context below.\n"
                "------------\n"
                "{text}\n"
                "------------\n"
                "Given the new context, refine the original summary in English"
                "If the context isn't useful, return the original summary."
            )
            
            
            refine_prompt = PromptTemplate.from_template(refine_template)
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="refine",
                question_prompt=prompt,
                refine_prompt=refine_prompt,
                return_intermediate_steps=True,
                input_key="input_documents",
                output_key="output_text",
            )
            result = chain({"input_documents": docs}, return_only_outputs=True)
            return result["output_text"]

        except Exception as e:
            raise fastapi.HTTPException(
                status_code=500,
                detail=f"Call to Azure OpenAI failed. Exception: {e}",
            )
            
    