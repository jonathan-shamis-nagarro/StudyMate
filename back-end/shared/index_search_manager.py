import os
from models.search_model import RetriveDocQueryFields
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import (
    VectorizedQuery,
    VectorQuery
)
from azure.search.documents.indexes.models import (  
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticPrioritizedFields,
    SemanticField,  
    SearchField,  
    SemanticSearch,
    VectorSearch,  
    HnswAlgorithmConfiguration,
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticField,  
    SearchField,  
    VectorSearch,  
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)

from shared.openai_manager import AzureOpenAIManager  

SEMANTIC_CONFIG_NAME: str = "pubsec-semantic-config"
VECTOR_CONFIG_NAME: str = "pubsec-vector-config"
VECTOR_SEARCH_PROFILE:str="pubsec-vector-profile"
HNSW_VECTOR_CONFIG: str = "hnsw-vector-config"
KNN_VECTOR_CONFIG: str = "exhaustive-knn-config"
KNN_VECTOR_PROFILE:str = "exhaustive-knn-profile"

class IndexSearchManager:
    def __init__(
        self
    ):
        self.endpoint = os.getenv("COGNITIVE_SEARCH_ENDPOINT")
        self.key = os.getenv("COGNITIVE_SEARCH_API_KEY")
        self.batch_size = 1000
        self.index_client = SearchIndexClient(
            endpoint = self.endpoint,
            credential=AzureKeyCredential(self.key),
        )
        self.index_name = os.getenv("COGNITIVE_SEARCH_INDEX_NAME")
        self.search_client = SearchClient(
            endpoint = self.endpoint,
            index_name = self.index_name,
            credential = AzureKeyCredential(self.key),
        )
        self.openai_wrapper = AzureOpenAIManager()

    def create_or_update_search_index(self):
        fields = []
        # search_index_fields = [field.to_dict() for field in search_index_fields]
        semantic_field: Any
        
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable = True,
                searchable = True,
                retrievable =  True,
                sortable = True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                retrievable=True,
            ),
            SearchField(
                name="contentVector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_configuration=VECTOR_CONFIG_NAME,
                vector_search_profile_name = VECTOR_SEARCH_PROFILE,
            ),
            SearchableField(
                name="fileName",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable = True,
                retrievable =  True,
                sortable = True,
            )
        ]
             
        # Configure the vector search configuration  
        vector_search = VectorSearch(
            algorithms = [
                HnswAlgorithmConfiguration(
                    name = HNSW_VECTOR_CONFIG,
                    kind = VectorSearchAlgorithmKind.HNSW,
                    parameters = HnswParameters(
                        m = 4,
                        ef_construction = 400,
                        ef_search = 500,
                        metric = VectorSearchAlgorithmMetric.COSINE
                    )
                ),
                ExhaustiveKnnAlgorithmConfiguration(
                    name = KNN_VECTOR_CONFIG,
                    kind = VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                    parameters = ExhaustiveKnnParameters(
                        metric = VectorSearchAlgorithmMetric.COSINE
                    )
                )
            ],
            profiles = [
                VectorSearchProfile(
                    name = VECTOR_SEARCH_PROFILE,
                    algorithm_configuration_name = HNSW_VECTOR_CONFIG,
                ),
                VectorSearchProfile(
                    name = KNN_VECTOR_PROFILE,
                    algorithm_configuration_name = KNN_VECTOR_CONFIG,
                )
            ]
        )
        semantic_field = SemanticField(field_name = "content")
        semantic_config = SemanticConfiguration(
            name = SEMANTIC_CONFIG_NAME,
            prioritized_fields = SemanticPrioritizedFields(
                title_field = None,
                content_fields = [semantic_field],
            ),
        )
        
        # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the search index with the semantic settings
        index = SearchIndex(
            name = self.index_name,
            fields = fields,
            vector_search = vector_search,
            semantic_search = semantic_search
        )
        result = self.index_client.create_or_update_index(index)

        print(f' {result.name} created')

        return result.name
        
        
    def upload_documents(self, documents: list[dict[str,Any]]) -> int:
        doc_count = 0
        doc_batch = []
        succeeded_count = 0
        for doc in documents:
            doc_count += 1
            doc_batch.append(doc)
            if doc_count % self.batch_size == 0:
                results = self.search_client.upload_documents(documents=doc_batch)
                succeeded_count += sum([1 for r in results if r.succeeded])
                doc_batch = []

        if len(doc_batch) > 0:
            results = self.search_client.upload_documents(documents=doc_batch)
            succeeded_count += sum([1 for r in results if r.succeeded])
        
        return succeeded_count
    
    def search_documents(self, doc_query: RetriveDocQueryFields) -> list[any]:
        query_filter = None
        final_results = []
        if doc_query.filter is not None:
            query_filter = doc_query.filter
        
        if doc_query.vector_filed_name is not None:
            vector_query = VectorizedQuery(
                vector = self.openai_wrapper.get_embeddings(doc_query.search_text), 
                k_nearest_neighbors = doc_query.number_of_documents_retrive, 
                fields = doc_query.vector_filed_name,
            )  
            
            results = self.search_client.search(
                search_text = doc_query.search_text,
                vector_queries = [vector_query],
                filter = query_filter,
                select = doc_query.selected_fields,
                query_type = "semantic",
                semantic_configuration_name = SEMANTIC_CONFIG_NAME,
                query_caption = "extractive",
                query_answer = "extractive",
                top = doc_query.number_of_documents_retrive,
            ) 
            
            if(doc_query.selected_fields is not None):
                for result in results:
                    data ={
                        "Score": result['@search.score']
                    }
                    for field in doc_query.selected_fields:
                        data[field] = result[field]
                    final_results.append(data)
            else:
                return results.get_results()
        else:
            results = list(self.search_client.search(
                search_text = doc_query.search_text,
                filter = query_filter,
                select = doc_query.selected_fields,
                query_type = "semantic",
                semantic_configuration_name = SEMANTIC_CONFIG_NAME,
                query_caption = "extractive",
                query_answer = "extractive",
                top = doc_query.number_of_documents_retrive,
            ))
            
            if(doc_query.selected_fields is not None):                    
                for result in results:
                    data ={
                        "Score": result['@search.score']
                    }
                    for field in doc_query.selected_fields:
                        data[field] = result[field]
                    final_results.append(data)
            else:
                return results.get_results()
                    
        return final_results
    