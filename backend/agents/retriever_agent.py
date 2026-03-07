from backend.rag.text.retriever import text_retriever
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store

class RetrieverAgent:
    """
    Agent responsible for gathering evidence and context
    from the vector database using both text and image modalities.
    """
    
    def __init__(self):
        self.name = "Retriever Agent"
        self.role = "Gather diagnostic evidence from medical literature and patient history."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the retrieval logic.
        input_data expects: {"text_query": str, "image": Optional[PIL.Image]}
        """
        text_query = input_data.get("text_query", "")
        image = input_data.get("image")
        
        # Retrieve text context
        text_results = await text_retriever.retrieve(query=text_query, top_k=5)
        text_context = "\n\n".join([res['document'] for res in text_results]) if text_results else "No relevant text documents found."
        
        # Retrieve image context if provided
        image_context = "No relevant image context found."
        if image:
            image_embedding = await clip_embedder.embed_image(image)
            image_results = await vector_store.query_image(query_embedding=image_embedding, n_results=3)
            if image_results and image_results.get("metadatas") and image_results["metadatas"][0]:
                image_contexts = []
                for meta in image_results["metadatas"][0]:
                    if "description" in meta:
                        image_contexts.append(meta["description"])
                if image_contexts:
                    image_context = "\n".join(image_contexts)
                    
        return {
            "text_context": text_context,
            "image_context": image_context
        }

retriever_agent = RetrieverAgent()
