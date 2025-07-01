#!/usr/bin/env python3
"""
Lightning Fast Face Matcher API
Ultra-fast, minimal face matching with 7000 faces pre-loaded
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import faiss
import json
import os
from PIL import Image
import io
from deepface import DeepFace

# Initialize FastAPI
app = FastAPI(title="Lightning Fast Face Matcher", version="1.0.0")

# Global variables
embeddings = None
metadata = []
faiss_index = None
config = {"embedding_dim": 512, "model": "ArcFace"}

def load_database():
    """Load the lightning fast database"""
    global embeddings, metadata, faiss_index
    
    db_path = "../databases/lightning_fast_db.json"
    if not os.path.exists(db_path):
        db_path = "databases/lightning_fast_db.json"
    
    if not os.path.exists(db_path):
        return False
    
    with open(db_path, 'r') as f:
        data = json.load(f)
    
    embeddings = np.array(data['embeddings'], dtype='float32')
    metadata = data['metadata']
    
    # Build FAISS index
    faiss_index = faiss.IndexFlatIP(config['embedding_dim'])
    faiss_index.add(embeddings)
    
    return True

def get_face_embedding(image_bytes):
    """Extract face embedding from image bytes - ArcFace accuracy"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(img)
        
        result = DeepFace.represent(
            img_path=img_np, 
            model_name=config["model"],
            enforce_detection=True,  # Match ArcFace API accuracy
            detector_backend='opencv'
        )
        
        if not result:
            return None
        
        # Same normalization as ArcFace API
        embedding = np.array(result[0]['embedding'], dtype='float32')
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    except Exception as e:
        return None

# Load database on startup
if not load_database():
    print("❌ Database not found!")
    exit(1)

@app.get("/")
def root():
    return {
        "status": "⚡ LIGHTNING FAST",
        "total_faces": len(embeddings),
        "unique_persons": len(set(m['person'] for m in metadata)),
        "endpoints": {
            "search": "POST /search - Fast face matching"
        }
    }

@app.post("/search")
def search_face(
    file: UploadFile = File(...),
    top_k: int = 5,
    threshold: float = 0.68  # Match ArcFace threshold
):
    """Ultra-fast face search with ArcFace accuracy"""
    try:
        # Get embedding
        image_bytes = file.file.read()
        query_embedding = get_face_embedding(image_bytes)
        
        if query_embedding is None:
            raise HTTPException(status_code=400, detail="No face detected")
        
        # Fast FAISS search
        scores, indices = faiss_index.search(
            np.expand_dims(query_embedding, 0), 
            min(top_k, len(embeddings))
        )
        
        # Build results with same scoring as ArcFace
        results = []
        for i in range(len(scores[0])):
            idx = indices[0][i]
            score = float(scores[0][i])
            
            # Convert to distance and confidence like ArcFace API
            distance = 1 - score
            confidence = max(0, score * 100)
            is_match = distance < (1 - threshold)
            
            result = {
                "person": metadata[idx].get("person", "unknown"),
                "confidence": round(confidence, 2),
                "distance": round(distance, 4),
                "is_match": is_match,
                "rank": i + 1
            }
            if "image_path" in metadata[idx]:
                result["image_path"] = metadata[idx]["image_path"]
            results.append(result)
        
        return {
            "matches": results,
            "total_searched": len(embeddings),
            "threshold": threshold,
            "debug_info": {
                "top_3_raw_scores": [float(scores[0][i]) for i in range(min(3, len(scores[0])))],
                "query_embedding_norm": float(np.linalg.norm(query_embedding))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Lightning Fast API - {len(embeddings)} faces loaded")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
