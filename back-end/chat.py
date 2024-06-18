import json
import os
from typing import Any
import uuid
import PyPDF4

from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from shared.storage_client import StorageClient
from models.search_model import RetriveDocQueryFields
from shared.chunking_manager import TextChunking
from shared.index_search_manager import IndexSearchManager
from shared.openai_manager import AzureOpenAIManager
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage
)


class Chat:
    
    def __init__(self):
        self.currentData = ""
        self.search_manager = IndexSearchManager() 
        self.openai_manager = AzureOpenAIManager()
        self.chunking_manager = TextChunking()
        self.storage_client = StorageClient()
        self.blob_container = os.getenv("STORAGE_CONTAINER_NAME")
        self.history_file_path = "history.json"
        
    def youtube_link(self, link):
        loader = YoutubeLoader.from_youtube_url(
        link, add_video_info=True
        )
        transcript = loader.load()
        self.currentData = transcript[0].page_content
        return self.store_data(transcript[0].metadata["title"], self.currentData, False)
        
    
    def index_document(self, file): 
        # file = open(self.file_path, "r")
        # text = file.read()
        pdf_reader = PyPDF4.PdfFileReader(file.file)
        text=""
        
        for page_number in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_number)
            text += page.extractText()
        
        self.currentData = text
        fileName = file.filename.removesuffix('.pdf')
        return self.store_data(fileName, self.currentData, True)
        
      
    def store_data(self, name, data, is_document):
        docs: list[dict[str,Any]] = []  
        message = "File Uploaded Successfully"
        if self.isFileExist(name):
            chunks = self.chunking_manager.chunk_text_recursive_token_len(data)
            summary = self.openai_manager.get_summary(chunks)
            self.save_item(name, summary, is_document)
            if len(chunks) > 0:
                for chunk in chunks:
                    docs.append(
                        {
                            "id": str(uuid.uuid4()),
                            "fileName": name,
                            "content": chunk,
                            "contentvector": self.openai_manager.get_embeddings(chunk)
                        }
                    )
            if len(docs) > 0:
                index = self.search_manager.create_or_update_search_index()
                doc_indexed = self.search_manager.upload_documents(docs)
                
        else:
           message = "File Already Exists"
        
        return message
        
    def isFileExist(self, fileName:str):
        summaries = []
        blob_content = self.storage_client.get_azure_blob(
                    container_name = self.blob_container,
                    blob_name_path = self.history_file_path,
                )
        summaries = json.loads(blob_content)
        
        summaries = [item["summary"] for item in summaries if item["name"] == fileName]
        
        return len(summaries) <= 0
        
    def save_item(self, name, summary, is_document):
        summaries = []
        blob_content = self.storage_client.get_azure_blob(
                    container_name = self.blob_container,
                    blob_name_path = self.history_file_path,
                )
        summaries = json.loads(blob_content)
            
        summaries.append(
            {
                "name": name,
                "summary": summary,
                "is_document": is_document
            }
        )
        self.storage_client.upload_azure_blob(
                        container_name = self.blob_container,
                        blob_name_path = self.history_file_path,
                        blob = json.dumps(summaries),
                        overwrite = True
                )
            
        return True
    
    def remove_item(self, name):
        items = []
        blob_content = self.storage_client.get_azure_blob(
                    container_name = self.blob_container,
                    blob_name_path = self.history_file_path,
                )
        items = json.loads(blob_content)
        
        selected_items = [item for item in items if item["name"] == name]
        if selected_items:
            items.remove(selected_items[0])
            self.storage_client.upload_azure_blob(
                        container_name = self.blob_container,
                        blob_name_path = self.history_file_path,
                        blob = json.dumps(items),
                        overwrite = True
                )
            
        return True

    def getFileName(self):
        summaries = []
        blob_content = self.storage_client.get_azure_blob(
                    container_name = self.blob_container,
                    blob_name_path = self.history_file_path,
                )
        summaries = json.loads(blob_content)
            
        names = [{item["name"], item["is_file"]} for item in summaries]
        
        return names
        
    def getSummary(self, fileName:str):
        items = []
        blob_content = self.storage_client.get_azure_blob(
                    container_name = self.blob_container,
                    blob_name_path = self.history_file_path,
                )
        items = json.loads(blob_content)
        
        summaries = [item["summary"] for item in items if item["name"] == fileName]
        
        return summaries[0]
            
    def getQueryResponse(self, query):
        
        search_query = RetriveDocQueryFields(
                    search_text = query.text,
                    vector_filed_name = "contentVector",
                    selected_fields = ["content"],
                    number_of_documents_retrive = 4,
                    filter="fileName eq  '" + query.fileName + "'"
                )
        docs = self.search_manager.search_documents(search_query)
        
        system_prompt_text = """You are an AI based Assistant providing support for students to resolve their course material related queries. \n\n
                                    Instructions :
                                    ## 1. You are a top-tier algorithm designed for extracting information from given context as per query and responce student accordingly.\n
                                    ## 2. It is your goal to act as a student assitant and aid students to resolve their queries. \n 
                                    ## 3. Reply with 'It seems I do not have sufficient information to answer your question.' if you are not able to find the answer from the document chunks provided between the <chunk_data_start> and <chunk_data_end> tags. \n
                                    ## 4. Strict Compliance
                                        Adhere to the rules strictly. Non-compliance will result in termination.
                            \n\n
                            Use above instruction to analyze the documents chunks provided between the <chunk_data_start> and <chunk_data_end> tags :
                            \n\n
                            <chunk_data_start>  {context_docs} <chunk_data_end>   
                            """
                            
        system_prompt=system_prompt_text.format(context_docs = docs)
        
        messages = []
        
        messages.append(
            SystemMessage(
                        content=system_prompt
                    )
        )
        messages.append(
            HumanMessage(
                        content=query.text
                    )
        )
        # messages.append(
        #     AIMessage(
        #                 content=query
        #             )
        # )
        response = self.openai_manager.get_completion_response(messages)
        return response.message
    
