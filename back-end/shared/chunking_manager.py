import os
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextChunking:
    def __init__(
        self
    ):
        self.encoding_name = os.getenv("TIKTOKEN_ENCODING_NAME")
        self.chunk_size = 500
        self.chunk_overlap = 0
        self.is_separator_regex = True
        self.separators = ["."]

    @staticmethod
    def length_function(encoding_name,text) -> int:
        return len(tiktoken.get_encoding(encoding_name).encode(text, disallowed_special=()))

    def chunk_text_recursive_token_len(self,text) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            length_function = lambda x: self.length_function(self.encoding_name,x),
            is_separator_regex = self.is_separator_regex,
            separators = self.separators
        )
        chunks = text_splitter.split_text(text)
        return chunks