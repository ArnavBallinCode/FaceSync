#!/usr/bin/env python3
"""
FaceSync - Image Flattener
Flattens nested directory structure to root level for processing

Copyright (c) 2025 Arnav Angarkar. All rights reserved.
Author: Arnav Angarkar

PROPRIETARY AND CONFIDENTIAL
This software and its documentation are proprietary to Arnav Angarkar.
"""

import os
import shutil
import sys
import json
from pathlib import Path

def flatten_images():
    """Flatten all images from subdirectories to root Testing images folder"""
    
    IMAGES_DIR = "Testing images"
    
    try:
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
        
        moved_count = 0
        errors = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(IMAGES_DIR):
            # Skip the root directory itself
            if root == IMAGES_DIR:
                continue
                
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(IMAGES_DIR, file)
                    
                    # Handle filename conflicts
                    counter = 1
                    original_dest = dest_path
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(original_dest)
                        dest_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    try:
                        shutil.move(source_path, dest_path)
                        moved_count += 1
                    except Exception as e:
                        errors.append(f"Failed to move {source_path}: {str(e)}")
        
        # Remove empty subdirectories
        for root, dirs, files in os.walk(IMAGES_DIR, topdown=False):
            if root != IMAGES_DIR:
                try:
                    if not os.listdir(root):  # Directory is empty
                        os.rmdir(root)
                except:
                    pass
        
        return {
            "status": "success",
            "moved_files": moved_count,
            "errors": errors,
            "message": f"Flattened {moved_count} images to root directory"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    result = flatten_images()
    print(json.dumps(result, indent=2))
