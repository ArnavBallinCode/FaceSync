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
import sys
import subprocess
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app with increased limits for batch uploads
app = FastAPI(
    title="DeepFace API with ArcFace",
    description="High-accuracy face recognition API using ArcFace model",
    version="2.0.0"
)

# Configure multipart limits for large batch uploads
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class MultipartLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Increase multipart limits for batch uploads
        if hasattr(request, "scope"):
            request.scope["multipart_max_parts"] = 10000
            request.scope["multipart_max_files"] = 10000
        return await call_next(request)

app.add_middleware(MultipartLimitMiddleware)

# Add CORS middleware after app is defined
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5500"] etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Serve static UI files from /ui so API endpoints are not overridden
import os
static_dir = "/app" if os.environ.get("DOCKER_ENV") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")


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
            "add_faces_multi": "POST /add_faces_multi - Add multiple faces using filenames as IDs",
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

@app.post('/add_faces_multi')
async def add_faces_multi(files: List[UploadFile] = File(...)):
    """
    Add multiple faces to the database using only files (browser multi-file upload).
    Uses filename (without extension) as the ID for each face.
    Args:
        files: List of image files containing faces
    Returns:
        JSON response with status and details for each image
    """
    import os
    global face_db, face_ids, face_metadata, index
    results = []
    added_count = 0
    for idx, file in enumerate(files):
        # Use filename (without extension) as ID
        filename = file.filename if file.filename else f"file_{idx}"
        id = os.path.splitext(filename)[0]
        if id in face_ids:
            results.append({
                "id": id,
                "status": "duplicate",
                "message": f"Face with ID '{id}' already exists. Skipped."
            })
            continue
        try:
            # Use the EXACT same pattern as add_face
            image_bytes = await file.read()
            result = get_embedding(image_bytes, filename)
            embedding = result["embedding"]
            metadata = {
                "added_time": time.time(),
                "image_name": filename,
                "processing_time": result["processing_time"],
                "model": result["model"]
            }
            face_db.append((id, embedding, metadata))
            face_ids.append(id)
            face_metadata.append(metadata)
            index.add(np.expand_dims(embedding, 0))
            added_count += 1
            results.append({
                "id": id,
                "status": "success",
                "message": f"Face for '{id}' added successfully."
            })
        except Exception as e:
            results.append({
                "id": id,
                "status": "error",
                "message": str(e)
            })
    save_database()
    return {
        "status": "batch complete",
        "added": added_count,
        "total": len(files),
        "results": results,
        "total_faces": len(face_db)
    }

@app.post('/batch_upload_from_ui')
async def batch_upload_from_ui():
    """Trigger batch upload script from UI"""
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "ui_batch_upload.py"
        ], capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "status": "error", 
                "message": f"Script failed: {result.stderr}"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post('/flatten_images_from_ui')
async def flatten_images_from_ui():
    """Trigger image flattening script from UI"""
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "ui_flatten_images.py"
        ], capture_output=True, text=True, timeout=300)  # 5 min timeout
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "status": "error", 
                "message": f"Script failed: {result.stderr}"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)