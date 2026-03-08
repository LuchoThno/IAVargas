"""Test simplificado sin Unicode"""
import sys
sys.path.insert(0, '.')

results = []

# Test imports
try:
    from memory_engine import (
        DocumentLoader, get_document_loader,
        TextChunker, ChunkConfig, chunk_text,
        SemanticSearch,
        RAGContextBuilder,
        embed, embed_batch,
        preload_model
    )
    results.append("PASS: Imports")
except Exception as e:
    results.append(f"FAIL: Imports - {e}")

# Test hashing
try:
    from memory_engine import get_file_hash_chunked
    h = get_file_hash_chunked("requirements.txt")
    results.append(f"PASS: Hashing - {h[:8]}...")
except Exception as e:
    results.append(f"FAIL: Hashing - {e}")

# Test chunking
try:
    chunks = chunk_text("Este es un texto. Tiene varias oraciones. Para probar.", chunk_size=30, overlap=5)
    results.append(f"PASS: Chunking - {len(chunks)} chunks")
except Exception as e:
    results.append(f"FAIL: Chunking - {e}")

# Test preload
try:
    preload_model()
    results.append("PASS: Preload model")
except Exception as e:
    results.append(f"FAIL: Preload - {e}")

# Test embeddings
try:
    emb = embed("test")
    results.append(f"PASS: Embed - shape {emb.shape}")
except Exception as e:
    results.append(f"FAIL: Embed - {e}")

# Test batch
try:
    embs = embed_batch(["a", "b", "c"])
    results.append(f"PASS: Batch - shape {embs.shape}")
except Exception as e:
    results.append(f"FAIL: Batch - {e}")

# Test search
try:
    se = SemanticSearch()
    se.index_documents(["doc1", "doc2", "doc3"])
    rs = se.search("query", k=2)
    results.append(f"PASS: Search - {len(rs)} results")
except Exception as e:
    results.append(f"FAIL: Search - {e}")

# Test RAG builder
try:
    rb = RAGContextBuilder()
    ctx = rb.build_context([{"text": "test", "score": 0.9, "metadata": {}}], "query")
    results.append(f"PASS: RAG - {len(ctx)} chars")
except Exception as e:
    results.append(f"FAIL: RAG - {e}")

# Save results
with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Test results saved to test_results.txt")

