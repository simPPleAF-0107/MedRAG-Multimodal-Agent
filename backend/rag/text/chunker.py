import re

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the Text Chunker with specific size and overlap.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        """
        Split a document string into overlapping chunks.
        (A simple word-based splitting logic, easily upgradeable to LangChain/LlamaIndex chunkers)
        """
        # Basic cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split(" ")
        
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            # Move forward by (chunk_size - chunk_overlap)
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks

text_chunker = TextChunker()
