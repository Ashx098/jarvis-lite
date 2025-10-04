import os, argparse, chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import re
from typing import List, Tuple


EMBED = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_DIR = os.getenv("CHROMA_DIR", ".chroma")

# Enhanced chunking parameters
CHUNK_SIZE = 200  # tokens per chunk (smaller for better granularity)
CHUNK_OVERLAP = 50  # tokens overlap between chunks
MIN_CHUNK_SIZE = 30  # minimum chunk size


model = SentenceTransformer(EMBED)
client = chromadb.PersistentClient(path=CHROMA_DIR)
col = client.get_or_create_collection("jarvis_knowledge")


def smart_chunk_text(text: str, source_path: str) -> List[Tuple[str, dict]]:
    """Enhanced chunking with overlap and semantic boundaries"""
    chunks = []
    
    # Clean text but preserve some structure
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Try to split by sentences first, then by word count
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        # Fallback: split by words if no sentences found
        words = text.split()
        sentences = []
        for i in range(0, len(words), CHUNK_SIZE):
            sentence = ' '.join(words[i:i+CHUNK_SIZE])
            sentences.append(sentence)
    
    current_chunk = ""
    chunk_id = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        current_words = current_chunk.split()
        
        # If adding this sentence exceeds chunk size, save current chunk
        if len(current_words) + len(sentence_words) > CHUNK_SIZE and current_chunk.strip():
            if len(current_words) >= MIN_CHUNK_SIZE:
                chunks.append((current_chunk.strip(), {
                    "source": source_path,
                    "chunk_id": chunk_id,
                    "paragraph_count": 1,
                    "word_count": len(current_words)
                }))
                chunk_id += 1
            
            # Start new chunk with overlap
            if len(current_words) > CHUNK_OVERLAP:
                overlap_words = current_words[-CHUNK_OVERLAP:]
                current_chunk = " ".join(overlap_words) + " " + sentence + " "
            else:
                current_chunk = sentence + " "
        else:
            # Add sentence to current chunk
            current_chunk += sentence + ". "
    
    # Don't forget the last chunk
    if len(current_chunk.strip()) >= MIN_CHUNK_SIZE:
        chunks.append((current_chunk.strip(), {
            "source": source_path,
            "chunk_id": chunk_id,
            "paragraph_count": 1,
            "word_count": len(current_chunk.split())
        }))
    
    return chunks




def load_texts(root="knowledge"):
    docs = []
    for dirpath,_,files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath,f)
            if f.lower().endswith(".pdf"):
                txt = "\n\n".join(page.extract_text() or "" for page in PdfReader(p).pages)
            elif f.lower().endswith((".md",".txt")):
                txt = open(p, "r", encoding="utf-8", errors="ignore").read()
            else:
                continue
            docs.append((p, txt))
    return docs




def rebuild():
    docs = load_texts()
    if not docs:
        print("No docs found in ./knowledge")
        return
    # Clear all existing documents
    try:
        col.delete()
    except:
        # If collection doesn't exist or is empty, recreate it
        pass
    
    # Use smart chunking
    all_chunks = []
    all_ids = []
    all_metas = []
    
    for doc_path, doc_text in docs:
        chunks = smart_chunk_text(doc_text, doc_path)
        for chunk_text, chunk_meta in chunks:
            all_chunks.append(chunk_text)
            all_ids.append(f"{doc_path}_{chunk_meta['chunk_id']}")
            all_metas.append(chunk_meta)
    
    # Create embeddings for all chunks
    print(f"Creating embeddings for {len(all_chunks)} chunks...")
    embs = model.encode(all_chunks, convert_to_numpy=True)
    
    # Add to ChromaDB
    col.add(ids=all_ids, documents=all_chunks, metadatas=all_metas, embeddings=embs)
    print(f"Indexed {len(docs)} documents into {len(all_chunks)} chunks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if args.rebuild:
        rebuild()
