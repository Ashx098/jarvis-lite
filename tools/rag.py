import os, chromadb
from sentence_transformers import SentenceTransformer
import re
from typing import List, Dict, Tuple
import numpy as np


EMBED = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_DIR = os.getenv("CHROMA_DIR", ".chroma")


_model = None
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_col = _client.get_or_create_collection("jarvis_knowledge")


# Query expansion terms for better semantic matching
QUERY_EXPANSIONS = {
    "quality": ["accuracy", "performance", "evaluation", "results", "metrics", "assessment"],
    "good": ["effective", "accurate", "reliable", "successful", "performance", "results"],
    "paper": ["research", "study", "document", "article", "publication"],
    "medimatch": ["medicine", "medical", "healthcare", "disease", "symptom", "prediction"],
    "findings": ["results", "conclusions", "outcomes", "discoveries", "evaluation"],
    "method": ["methodology", "approach", "technique", "algorithm", "process"]
}


def _embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED)
    return _model


def expand_query(query: str) -> str:
    """Expand query with related terms for better semantic matching"""
    expanded_terms = []
    query_lower = query.lower()
    
    # Add expansion terms for matching keywords
    for keyword, expansions in QUERY_EXPANSIONS.items():
        if keyword in query_lower:
            expanded_terms.extend(expansions)
    
    # Also check for partial matches
    for keyword, expansions in QUERY_EXPANSIONS.items():
        for expansion in expansions:
            if expansion in query_lower:
                expanded_terms.append(keyword)
                break
    
    # Combine original query with expanded terms
    if expanded_terms:
        expanded_query = query + " " + " ".join(expanded_terms[:3])  # Limit to avoid noise
        return expanded_query
    
    return query


def calculate_relevance_score(doc: str, query: str, metadata: dict) -> float:
    """Calculate relevance score for better ranking"""
    score = 0.0
    doc_lower = doc.lower()
    query_lower = query.lower()
    
    # Exact phrase matches (highest weight)
    if query_lower in doc_lower:
        score += 2.0
    
    # Individual word matches
    query_words = set(query_lower.split())
    doc_words = set(doc_lower.split())
    word_overlap = len(query_words.intersection(doc_words))
    score += word_overlap * 0.5
    
    # Boost for chunks with numbers/percentages (likely results)
    if re.search(r'\d+%', doc):
        score += 0.8
    
    # Boost for chunks with evaluation terms
    eval_terms = ["accuracy", "precision", "recall", "f1", "performance", "results", "evaluation"]
    for term in eval_terms:
        if term in doc_lower:
            score += 0.3
    
    # Boost for methodology sections
    method_terms = ["method", "approach", "algorithm", "technique", "methodology"]
    for term in method_terms:
        if term in doc_lower:
            score += 0.2
    
    # Length penalty (prefer concise, relevant chunks)
    word_count = metadata.get("word_count", len(doc.split()))
    if word_count > 300:
        score -= 0.1
    elif word_count < 50:
        score -= 0.2
    
    return score


def query(q: str, k: int = 4) -> List[Tuple[str, dict]]:
    """Enhanced query with better semantic matching and ranking"""
    # Expand query for better semantic matching
    expanded_query = expand_query(q)
    
    # Get more results initially for better re-ranking
    initial_k = min(k * 3, 20)  # Get more candidates
    e = _embedder().encode([expanded_query])[0]
    res = _col.query(query_embeddings=[e], n_results=initial_k)
    
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    distances = res.get("distances", [[]])[0]
    
    # Calculate enhanced relevance scores
    candidates = []
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
        # Combine semantic similarity with relevance scoring
        semantic_score = 1.0 / (1.0 + dist)  # Convert distance to similarity
        relevance_score = calculate_relevance_score(doc, q, meta)
        
        # Weighted combination
        final_score = 0.6 * semantic_score + 0.4 * relevance_score
        
        candidates.append({
            "doc": doc,
            "meta": meta,
            "score": final_score,
            "semantic_score": semantic_score,
            "relevance_score": relevance_score
        })
    
    # Sort by final score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top k results with enhanced metadata
    results = []
    for candidate in candidates[:k]:
        meta = candidate["meta"].copy()
        meta["relevance_score"] = round(candidate["relevance_score"], 3)
        meta["semantic_score"] = round(candidate["semantic_score"], 3)
        meta["final_score"] = round(candidate["score"], 3)
        results.append((candidate["doc"], meta))
    
    return results


def query_for_agent(q: str, k: int = 4) -> List[Tuple[str, str]]:
    """RAG query function that returns the format expected by the agent"""
    enhanced_results = query(q, k)
    # Convert to old format (document, path) for agent compatibility
    agent_results = []
    for doc, meta in enhanced_results:
        path = meta.get("source", "Unknown")
        agent_results.append((doc, path))
    return agent_results
