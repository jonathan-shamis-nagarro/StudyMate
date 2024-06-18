import io
import os
from typing import Any
from azure.storage.blob import BlobServiceClient



class StorageClient():
    def __init__(
        self
    ) -> None:
        self.container_name = os.getenv("STORAGE_CONTAINER_NAME")
        self.storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
        self.storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
        self.storage_connection_string = "DefaultEndpointsProtocol=https;AccountName="+self.storage_account_name+";AccountKey="+self.storage_account_key+";EndpointSuffix=core.windows.net"
        
        self.blob_service_client = BlobServiceClient.from_connection_string(self.storage_connection_string)

    
    def get_azure_blob(
        self, 
        container_name: str, 
        blob_name_path: str
    ) -> Any:
        
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name_path)
        if blob_client.exists():            
            blob_download = blob_client.download_blob()
            blob_content = blob_download.readall()           
            return blob_content
        else:
            raise Exception("blob -> "+blob_name_path+" not exist!!")
        
    def get_azure_blob_list(
        self, 
        container_name: str, 
        blob_name_path: str
    ) -> Any:
        container_client = self.blob_service_client.get_container_client(container_name)
        if container_client.exists():
            blob_list = container_client.list_blobs(name_starts_with=blob_name_path)
            return blob_list
        else:
            raise Exception("blob -> "+blob_name_path+" not exist!!")
    
    def upload_azure_blob(
        self, 
        container_name: str, 
        blob_name_path: str,
        blob: bytes | str,
        overwrite: bool = True
    ) -> Any:
        
        container_client = self.blob_service_client.get_container_client(container_name)
        if container_client.exists() == False:
            container_client.create_container()
        blob_client = container_client.get_blob_client(blob_name_path)
        try:
            blob_client.upload_blob(blob, overwrite = overwrite)
        except Exception as e:
            raise Exception("blob -> "+blob_name_path+" not exist!!")
        
    def delete_azure_blob(
        self, 
        container_name: str, 
        blob_name_path: str
    ) -> Any:
        
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name_path)
        if blob_client.exists():            
            blob_download = blob_client.delete_blob()
            return blob_download
        else:
            raise Exception("blob -> "+blob_name_path+" not exist!!")
        
    def is_blob_exist(
        self, 
        container_name: str, 
        blob_name_path: str
    ) -> Any:
        
        blob_client = self.blob_service_client.get_blob_client(container_name,blob_name_path)
        return blob_client.exists()
    
    def is_blob_container_exist(
        self, 
        container_name: str
    ) -> Any:
        container_client = self.blob_service_client.get_container_client(container_name)
        return container_client.exists()