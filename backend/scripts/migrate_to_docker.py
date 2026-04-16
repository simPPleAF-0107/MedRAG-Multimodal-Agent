import os
import asyncio
import logging
from qdrant_client import QdrantClient
from backend.config import settings

logger = logging.getLogger(__name__)

def migrate_qdrant_to_docker():
    print("======================================================================")
    print("  🚀 MedRAG Local -> Docker Qdrant Migrator")
    print("======================================================================")
    
    local_db_path = settings.QDRANT_DB_DIR
    if not os.path.exists(local_db_path):
        print(f"❌ Local database not found at {local_db_path}. Nothing to migrate.")
        return

    print("🔌 Connecting to Local Qdrant Engine...")
    local_client = QdrantClient(path=local_db_path)
    
    print("🔌 Connecting to Docker Qdrant Engine (localhost:6333)...")
    docker_url = "http://localhost:6333"
    try:
        docker_client = QdrantClient(url=docker_url)
        # Ping test
        colls = docker_client.get_collections()
    except Exception as e:
        print(f"❌ Failed to connect to Docker Qdrant at {docker_url}. Is Docker running?")
        print(f"Error: {e}")
        return

    collections = local_client.get_collections().collections
    if not collections:
        print("✅ No collections found in local DB. Migration complete.")
        return

    for col in collections:
        col_name = col.name
        print(f"\n📦 Migrating collection: {col_name}...")
        
        # Get count
        col_details = local_client.get_collection(col_name)
        total_points = col_details.points_count
        print(f"   📊 Local points detected: {total_points}")
        
        if total_points == 0:
            continue
            
        # Recreate collection cleanly in Docker if missing
        if not docker_client.collection_exists(col_name):
            print(f"   ⚙️ Re-creating {col_name} on Docker server...")
            vectors_config = col_details.config.params.vectors
            docker_client.create_collection(
                collection_name=col_name,
                vectors_config=vectors_config
            )
            
        # Stream points using scroll API
        migrated = 0
        offset = None
        
        from qdrant_client.models import PointStruct
        while migrated < total_points:
            records, next_page_offset = local_client.scroll(
                collection_name=col_name,
                limit=1000,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )
            
            if not records:
                break
                
            # Convert Record returned by scroll() into PointStruct required by upsert()
            points = [
                PointStruct(id=r.id, vector=r.vector, payload=r.payload)
                for r in records
            ]
                
            # Upsert into Docker
            docker_client.upsert(
                collection_name=col_name,
                points=points
            )
            
            migrated += len(records)
            offset = next_page_offset
            
            print(f"      ✅ Transferred {migrated} / {total_points} vectors...")
            
            if next_page_offset is None:
                break

    print("\n======================================================================")
    print("  🏁 MIGRATION COMPLETE! Your local vectors are now inside Docker!")
    print("======================================================================")


if __name__ == "__main__":
    migrate_qdrant_to_docker()
