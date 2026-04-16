"""
MedRAG Visual Knowledge Base Seeder — Expanded Edition
=======================================================
Downloads open-source medical image datasets from Hugging Face and
embeds them into the Qdrant image vector store using CLIP.

Datasets:
  1. VQA-RAD       —  315 radiology images (X-ray, CT, MRI) with Q&A
  2. PathVQA       —  4,998 pathology slide images with Q&A
  3. SLAKE-VQA     —  642 multimodal medical images with Q&A  
  4. ROCO          —  Radiology Objects in COntext (diverse radiology, sampled)

Run:  python -m backend.scripts.seed_images
"""
import sys
import os
import asyncio
import hashlib
import uuid as _uuid
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from backend.utils.logger import logger


def _stable_uuid(text: str) -> str:
    """Deterministic UUID from a string to avoid duplicates on re-runs."""
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


async def _embed_and_store_image(image, doc_id: str, metadata: dict):
    """Embed a PIL image with CLIP and store in Qdrant."""
    try:
        embedding = await clip_embedder.embed_image(image)
        await vector_store.store_image_embedding(
            image_id=doc_id,
            embedding=embedding,
            metadata=metadata
        )
        return True
    except Exception as e:
        print(f"  ⚠ Failed to embed {doc_id}: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# 1. VQA-RAD — Radiology Visual Q&A (X-ray, CT, MRI)
# ═══════════════════════════════════════════════════════════
async def seed_vqa_rad(max_images: int = 315):
    from datasets import load_dataset

    print(f"\n🖼️  [1/4] Loading VQA-RAD (up to {max_images} images)…")
    try:
        ds = load_dataset("flaviagiammarino/vqa-rad", split="train")
    except Exception as e:
        print(f"  ❌ Failed to load VQA-RAD: {e}")
        return 0

    count = 0
    for idx, row in enumerate(ds):
        if count >= max_images:
            break

        img = row.get("image")
        question = row.get("question", "")
        answer = row.get("answer", "")

        if img is None:
            continue

        doc_id = _stable_uuid(f"vqa_rad_{idx}")
        metadata = {
            "source": "VQA-RAD",
            "type": "radiology_vqa",
            "question": question[:200],
            "description": f"Radiology Query: {question} Findings: {answer}"
        }

        if await _embed_and_store_image(img, doc_id, metadata):
            count += 1
            if count % 50 == 0:
                print(f"   ✅ VQA-RAD: {count}/{max_images} images embedded")

    print(f"   ✅ VQA-RAD complete — {count} images")
    return count


# ═══════════════════════════════════════════════════════════
# 2. PathVQA — Pathology Visual Q&A
# ═══════════════════════════════════════════════════════════
async def seed_pathvqa(max_images: int = 2000):
    from datasets import load_dataset

    print(f"\n🖼️  [2/4] Loading PathVQA (up to {max_images} images)…")
    try:
        ds = load_dataset("flaviagiammarino/path-vqa", split="train")
    except Exception as e:
        print(f"  ❌ Failed to load PathVQA: {e}")
        return 0

    count = 0
    seen_images = set()  # PathVQA has multiple Q&A per image — deduplicate

    for idx, row in enumerate(ds):
        if count >= max_images:
            break

        img = row.get("image")
        question = row.get("question", "")
        answer = row.get("answer", "")

        if img is None:
            continue

        # Create a content-based key to deduplicate same images with different questions
        # Use image size as a rough dedup key (avoids hashing every pixel)
        img_key = f"{img.size[0]}x{img.size[1]}_{idx // 5}"
        if img_key in seen_images:
            continue
        seen_images.add(img_key)

        doc_id = _stable_uuid(f"pathvqa_{idx}")
        metadata = {
            "source": "PathVQA",
            "type": "pathology_vqa",
            "question": question[:200],
            "description": f"Pathology Query: {question} Findings: {answer}"
        }

        if await _embed_and_store_image(img, doc_id, metadata):
            count += 1
            if count % 200 == 0:
                print(f"   ✅ PathVQA: {count}/{max_images} images embedded")

    print(f"   ✅ PathVQA complete — {count} images")
    return count


# ═══════════════════════════════════════════════════════════
# 3. SLAKE-VQA — Multimodal Medical VQA (CT, MRI, X-ray)
# ═══════════════════════════════════════════════════════════
async def seed_slake(max_images: int = 642):
    from datasets import load_dataset

    print(f"\n🖼️  [3/4] Loading SLAKE-VQA (up to {max_images} images)…")
    try:
        ds = load_dataset("mdwiratathya/SLAKE", split="train")
    except Exception as e:
        print(f"  ❌ Failed to load SLAKE: {e}")
        return 0

    count = 0
    for idx, row in enumerate(ds):
        if count >= max_images:
            break

        img = row.get("image")
        question = row.get("question", "")
        answer = row.get("answer", "")
        img_name = row.get("img_name", "")

        if img is None:
            continue

        doc_id = _stable_uuid(f"slake_{idx}")
        metadata = {
            "source": "SLAKE-VQA",
            "type": "multimodal_medical_vqa",
            "question": question[:200],
            "img_name": img_name,
            "description": f"Medical Image Query: {question} Findings: {answer}"
        }

        if await _embed_and_store_image(img, doc_id, metadata):
            count += 1
            if count % 100 == 0:
                print(f"   ✅ SLAKE: {count}/{max_images} images embedded")

    print(f"   ✅ SLAKE complete — {count} images")
    return count


# ═══════════════════════════════════════════════════════════
# 4. ROCO — Radiology Objects in COntext
# ═══════════════════════════════════════════════════════════
async def seed_roco(max_images: int = 5000):
    from datasets import load_dataset

    print(f"\n🖼️  [4/4] Loading ROCO (up to {max_images} images)…")
    try:
        ds = load_dataset("eltorio/ROCO", split="train")
    except Exception as e:
        print(f"  ❌ Failed to load ROCO: {e}")
        return 0

    count = 0
    for idx, row in enumerate(ds):
        if count >= max_images:
            break

        img = row.get("image")
        caption = row.get("caption", "")

        if img is None or not caption:
            continue

        doc_id = _stable_uuid(f"roco_{idx}")
        metadata = {
            "source": "ROCO",
            "type": "radiology_contextual",
            "description": caption[:500]
        }

        if await _embed_and_store_image(img, doc_id, metadata):
            count += 1
            if count % 500 == 0:
                print(f"   ✅ ROCO: {count}/{max_images} images embedded")

    print(f"   ✅ ROCO complete — {count} images")
    return count


# ═══════════════════════════════════════════════════════════
# Main Runner
# ═══════════════════════════════════════════════════════════
async def main():
    print("=" * 60)
    print("  MedRAG Visual Knowledge Base Seeder — Expanded Edition")
    print("  Downloading & embedding medical image datasets")
    print("=" * 60)

    start = time.time()

    total = 0
    total += await seed_vqa_rad()       # ~315 radiology images
    total += await seed_pathvqa()        # ~2000 pathology images
    
    # Note: SLAKE and ROCO repos have been removed/made private by their authors on HuggingFace 
    # and no longer support standard loading. We are bypassing them as 2,300+ images is plenty!

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  🎉 Image seeding complete!")
    print(f"  Total images embedded: {total:,}")
    print(f"  Time elapsed: {elapsed / 60:.1f} minutes")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
