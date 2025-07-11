"""
Copyright (c) 2025 Arnav Angarkar. All rights reserved.
Author: Arnav Angarkar

PROPRIETARY AND CONFIDENTIAL
This software and its documentation are proprietary to Arnav Angarkar.
No part of this software may be copied, reproduced, distributed, transmitted,
transcribed, stored in a retrieval system, or translated into any human or
computer language, in any form or by any means, electronic, mechanical,
magnetic, optical, chemical, manual, or otherwise, without the express
written permission of Arnav Angarkar.

Unauthorized copying, distribution, or use of this software is strictly
prohibited and may result in severe civil and criminal penalties.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from deepface import DeepFace
import numpy as np
import faiss
from PIL import Image
import io
import os
import time
import json
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="DeepFace API with ArcFace",
    description="High-accuracy face recognition API using ArcFace model",
    version="2.0.0"
)

# Configuration
CONFIG = {
    "model_name": "ArcFace",  # Higher accuracy than Facenet
    "embedding_dim": 512,     # ArcFace embedding dimension
    "similarity_threshold": 0.68,  # Threshold for face matching (ArcFace optimized)
    "max_faces_per_image": 1,  # Only process single face per image
    "enforce_detection": True,  # Require face detection
}

# In-memory database
face_db = []      # [(id, embedding, metadata)]
face_ids = []     # [id1, id2, ...]
face_metadata = []  # [{"added_time": ..., "image_name": ...}, ...]

# FAISS index for fast similarity search
index = faiss.IndexFlatIP(CONFIG["embedding_dim"])  # Inner Product for cosine similarity

def get_embedding(image_bytes: bytes, image_name: str = "unknown") -> dict:
    """
    Extract face embedding from image bytes using ArcFace model
    
    Args:
        image_bytes: Raw image data
        image_name: Name of the image file for logging
    
    Returns:
        dict: Contains embedding, confidence, and metadata
    """
    try:
        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(img)
        
        # Get embedding using ArcFace model
        start_time = time.time()
        result = DeepFace.represent(
            img_path=img_np, 
            model_name=CONFIG["model_name"],
            enforce_detection=CONFIG["enforce_detection"]
        )
        processing_time = time.time() - start_time
        
        if not result:
            raise ValueError("No face detected in the image")
        
        # Get the first (and should be only) face embedding
        embedding = result[0]['embedding']
        
        # Normalize for cosine similarity (required for IndexFlatIP)
        embedding = np.array(embedding, dtype='float32')
        embedding = embedding / np.linalg.norm(embedding)
        
        return {
            "embedding": embedding,
            "processing_time": processing_time,
            "model": CONFIG["model_name"],
            "dimensions": len(embedding)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Face processing failed: {str(e)}")

def save_database():
    """Save face database to JSON file"""
    data = {
        "face_ids": face_ids,
        "face_db": [{"id": item[0], "embedding": item[1].tolist(), "metadata": item[2]} for item in face_db],
        "config": CONFIG
    }
    with open("arcface_database.json", "w") as f:
        json.dump(data, f, indent=2)

def load_database():
    """Load face database from JSON file"""
    global face_db, face_ids, face_metadata, index
    
    if os.path.exists("arcface_database.json"):
        try:
            with open("arcface_database.json", "r") as f:
                data = json.load(f)
            
            face_ids = data.get("face_ids", [])
            face_metadata = []
            
            # Reconstruct face_db
            for item in data.get("face_db", []):
                embedding = np.array(item["embedding"], dtype='float32')
                metadata = item["metadata"]
                face_db.append((item["id"], embedding, metadata))
                face_metadata.append(metadata)
            
            # Rebuild FAISS index
            if face_db:
                embeddings_array = np.array([item[1] for item in face_db], dtype='float32')
                index = faiss.IndexFlatIP(CONFIG["embedding_dim"])
                index.add(embeddings_array)
                
            print(f"Loaded {len(face_db)} faces from database")
            
        except Exception as e:
            print(f"Error loading database: {e}")

# Load existing database on startup
load_database()

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "DeepFace API with ArcFace - High Accuracy Face Recognition",
        "version": "2.0.0",
        "model": CONFIG["model_name"],
        "embedding_dimensions": CONFIG["embedding_dim"],
        "faces_in_database": len(face_db),
        "endpoints": {
            "add_face": "POST /add_face - Add a new face to the database",
            "match_face": "POST /match_face - Match a face against the database",
            "list_faces": "GET /list_faces - List all faces in database",
            "delete_face": "DELETE /delete_face/{id} - Delete a face from database",
            "stats": "GET /stats - Get detailed statistics"
        }
    }

@app.post('/add_face')
def add_face(id: str = Form(...), file: UploadFile = File(...)):
    """
    Add a new face to the database
    
    Args:
        id: Unique identifier for the person
        file: Image file containing the face
    
    Returns:
        JSON response with status and details
    """
    global face_db, face_ids, face_metadata, index
    
    # Check if ID already exists
    if id in face_ids:
        return JSONResponse(
            status_code=400,
            content={"error": f"Face with ID '{id}' already exists. Use a different ID."}
        )
    
    try:
        # Read image file
        image_bytes = file.file.read()
        
        # Get embedding
        result = get_embedding(image_bytes, file.filename)
        embedding = result["embedding"]
        
        # Add to database
        metadata = {
            "added_time": time.time(),
            "image_name": file.filename,
            "processing_time": result["processing_time"],
            "model": result["model"]
        }
        
        face_db.append((id, embedding, metadata))
        face_ids.append(id)
        face_metadata.append(metadata)
        
        # Add to FAISS index
        index.add(np.expand_dims(embedding, 0))
        
        # Save database
        save_database()
        
        return {
            "status": "success",
            "message": f"Face for '{id}' added successfully",
            "details": {
                "id": id,
                "model": result["model"],
                "dimensions": result["dimensions"],
                "processing_time": f"{result['processing_time']:.3f}s",
                "total_faces": len(face_db)
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post('/match_face')
def match_face(file: UploadFile = File(...), top_k: int = 1):
    """
    Match a face against the database
    
    Args:
        file: Image file containing the face to match
        top_k: Number of top matches to return
    
    Returns:
        JSON response with match results
    """
    global face_db, face_ids, index
    
    if len(face_db) == 0:
        raise HTTPException(status_code=400, detail="No faces in database. Add some faces first.")
    
    try:
        # Read image file
        image_bytes = file.file.read()
        
        # Get embedding
        result = get_embedding(image_bytes, file.filename)
        query_embedding = result["embedding"]
        
        # Search in FAISS index
        scores, indices = index.search(np.expand_dims(query_embedding, 0), min(top_k, len(face_db)))
        
        matches = []
        for i in range(len(scores[0])):
            idx = indices[0][i]
            score = float(scores[0][i])
            
            # Convert cosine similarity to distance (1 - similarity)
            distance = 1 - score
            confidence = max(0, score * 100)  # Convert to percentage
            
            face_id = face_ids[idx]
            metadata = face_metadata[idx]
            
            is_match = distance < (1 - CONFIG["similarity_threshold"])
            
            matches.append({
                "id": face_id,
                "distance": round(distance, 4),
                "confidence": round(confidence, 2),
                "is_match": is_match,
                "added_time": metadata["added_time"],
                "rank": i + 1
            })
        
        # Determine the best match
        best_match = matches[0] if matches else None
        
        return {
            "query_info": {
                "model": result["model"],
                "processing_time": f"{result['processing_time']:.3f}s",
                "dimensions": result["dimensions"]
            },
            "best_match": best_match,
            "all_matches": matches,
            "threshold": CONFIG["similarity_threshold"],
            "total_faces_searched": len(face_db)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get('/list_faces')
def list_faces():
    """List all faces in the database"""
    faces = []
    for i, (face_id, _, metadata) in enumerate(face_db):
        faces.append({
            "id": face_id,
            "index": i,
            "added_time": metadata["added_time"],
            "image_name": metadata.get("image_name", "unknown"),
            "model": metadata.get("model", CONFIG["model_name"])
        })
    
    return {
        "total_faces": len(faces),
        "faces": faces
    }

@app.delete('/delete_face/{face_id}')
def delete_face(face_id: str):
    """Delete a face from the database"""
    global face_db, face_ids, face_metadata, index
    
    if face_id not in face_ids:
        raise HTTPException(status_code=404, detail=f"Face with ID '{face_id}' not found")
    
    # Find and remove the face
    idx = face_ids.index(face_id)
    
    # Remove from all lists
    del face_db[idx]
    del face_ids[idx]
    del face_metadata[idx]
    
    # Rebuild FAISS index
    if face_db:
        embeddings_array = np.array([item[1] for item in face_db], dtype='float32')
        index = faiss.IndexFlatIP(CONFIG["embedding_dim"])
        index.add(embeddings_array)
    else:
        index = faiss.IndexFlatIP(CONFIG["embedding_dim"])
    
    # Save database
    save_database()
    
    return {
        "status": "success",
        "message": f"Face '{face_id}' deleted successfully",
        "remaining_faces": len(face_db)
    }

@app.get('/stats')
def get_stats():
    """Get detailed API statistics"""
    return {
        "database_stats": {
            "total_faces": len(face_db),
            "face_ids": face_ids
        },
        "model_info": {
            "name": CONFIG["model_name"],
            "embedding_dimensions": CONFIG["embedding_dim"],
            "similarity_threshold": CONFIG["similarity_threshold"]
        },
        "performance": {
            "faiss_index_size": index.ntotal if index else 0,
            "search_complexity": "O(n) for exact search"
        },
        "current_config": CONFIG
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)