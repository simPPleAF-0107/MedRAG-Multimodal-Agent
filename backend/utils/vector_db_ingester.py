import asyncio
from backend.database.db import AsyncSessionLocal, init_db
from backend.database.models import Report
from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder

async def ingest_database_to_vector_store():
    """
    Reads all existing reports from the database, generates text embeddings
    for the chief complaints and final reports, and stores them in ChromaDB.
    """
    # Ensure database tables exist and are accessible
    await init_db()
    print("Starting Vector DB Ingestion...")
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(Report))
        reports = result.scalars().all()
        
        if not reports:
            print("No reports found in the database. Run the data generator first.")
            return

        print(f"Found {len(reports)} reports to process.")
        
        processed_count = 0
        for report in reports:
            # We want to embed the rich context of the report
            text_to_embed = f"Patient Complaint: {report.chief_complaint}\\nReasoning: {report.diagnosis_reasoning}\\nFinal Assessment: {report.final_report}"
            
            # Generate the embedding using sentence-transformers (TextEmbedder)
            embedding = await text_embedder.embed_text(text_to_embed)
            
            # Store in VectorStore
            metadata = {
                "report_id": report.id,
                "patient_id": report.patient_id,
                "confidence_score": float(report.confidence_score) if report.confidence_score else 0.0,
                "risk_score": float(report.risk_score) if report.risk_score else 0.0,
                "emergency_flag": bool(report.emergency_flag)
            }
            
            # The VectorStore uses add() which requires string ID
            vector_id = f"report_{report.id}"
            await vector_store.store_text_embedding(
                doc_id=vector_id,
                embedding=embedding,
                text=text_to_embed,
                metadata=metadata
            )
            processed_count += 1
            if processed_count % 10 == 0:
                print(f"Processed {processed_count}/{len(reports)}...")
                
        print(f"Ingestion complete! Successfully added {processed_count} documents to ChromaDB.")
        
        # Verify ingestion by performing a test query
        print("\\nRunning sanity check query: 'chest pain'")
        test_embedding = await text_embedder.embed_text("chest pain")
        test_results = await vector_store.query_text(query_embedding=test_embedding, n_results=2)
        print("Query Results:")
        for idx, doc in enumerate(test_results['documents'][0]):
            print(f"- Match {idx+1}: {doc[:100]}...")

if __name__ == "__main__":
    asyncio.run(ingest_database_to_vector_store())
