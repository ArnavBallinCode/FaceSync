#!/usr/bin/env python3
"""
FaceSync - UI Batch Upload Handler
Automated batch upload script called from the web UI

Copyright (c) 2025 Arnav Angarkar. All rights reserved.
Author: Arnav Angarkar

PROPRIETARY AND CONFIDENTIAL
This software and its documentation are proprietary to Arnav Angarkar.
"""

import os
import sys
import requests
import json
from pathlib import Path

def run_batch_upload():
    """Run batch upload with conservative settings for UI calls"""
    API_URL = "http://localhost:8002/add_faces_multi"
    IMAGES_DIR = "Testing images"
    BATCH_SIZE = 100  # Conservative for UI stability
    
    try:
        # Get all image files
        all_files = [f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        total = len(all_files)
        
        if total == 0:
            return {"status": "error", "message": "No images found in Testing images folder"}
        
        results = {"batches": [], "total_uploaded": 0, "total_files": total}
        
        for i in range(0, total, BATCH_SIZE):
            batch_files = all_files[i:i+BATCH_SIZE]
            files = [("files", (fname, open(os.path.join(IMAGES_DIR, fname), "rb"))) for fname in batch_files]
            
            try:
                response = requests.post(API_URL, files=files, timeout=300)
                batch_result = {
                    "batch_num": i//BATCH_SIZE + 1,
                    "files_count": len(batch_files),
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    batch_result["added"] = data.get("added", 0)
                    results["total_uploaded"] += data.get("added", 0)
                
                results["batches"].append(batch_result)
                
            except Exception as e:
                results["batches"].append({
                    "batch_num": i//BATCH_SIZE + 1,
                    "files_count": len(batch_files),
                    "error": str(e),
                    "success": False
                })
            finally:
                for _, (_, f) in files:
                    f.close()
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = run_batch_upload()
    print(json.dumps(result, indent=2))
