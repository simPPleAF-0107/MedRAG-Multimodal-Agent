import re


class TextChunker:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 100):
        """
        Initialize the Text Chunker with specific size and overlap.

        Uses sentence-boundary-aware splitting to avoid cutting
        mid-sentence, which causes semantic fragmentation and
        increases hallucination in downstream LLM reasoning.

        Args:
            chunk_size:   Target number of words per chunk (300-500 recommended)
            chunk_overlap: Number of overlap words between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences using regex.
        Handles common abbreviations and decimal numbers to avoid false splits.
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            return []

        # Split on sentence-ending punctuation followed by space + capital letter or end
        # Negative lookbehind for common abbreviations (Dr., Mr., etc.)
        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z])',
            text
        )
        # Filter empty sentences
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, text: str) -> list[str]:
        """
        Split a document string into overlapping chunks at sentence boundaries.

        Strategy:
        1. Split text into sentences
        2. Accumulate sentences until chunk_size words are reached
        3. Create chunk, then backtrack by chunk_overlap words for the next chunk
        4. Never split mid-sentence
        """
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        chunks = []
        current_sentences = []
        current_word_count = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())

            # If a single sentence is longer than chunk_size, include it as-is
            if sentence_words >= self.chunk_size:
                # Flush current buffer first
                if current_sentences:
                    chunks.append(" ".join(current_sentences))
                chunks.append(sentence)
                current_sentences = []
                current_word_count = 0
                continue

            # If adding this sentence would exceed chunk_size, flush the buffer
            if current_word_count + sentence_words > self.chunk_size and current_sentences:
                chunks.append(" ".join(current_sentences))

                # Overlap: keep trailing sentences that fit within overlap budget
                overlap_sentences = []
                overlap_words = 0
                for s in reversed(current_sentences):
                    s_words = len(s.split())
                    if overlap_words + s_words > self.chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_words += s_words

                current_sentences = overlap_sentences
                current_word_count = overlap_words

            current_sentences.append(sentence)
            current_word_count += sentence_words

        # Flush remaining sentences
        if current_sentences:
            chunks.append(" ".join(current_sentences))

        return chunks


text_chunker = TextChunker()
