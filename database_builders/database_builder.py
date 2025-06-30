#!/usr/bin/env python3
"""
Professional Database Builder
Recursively scans all image folders and adds new images to the lightning fast database.
Supports incremental updates - only processes new images not already in the database.
"""
import os
import json
import time
import numpy as np
from deepface import DeepFace
import faiss
from pathlib import Path

class DatabaseBuilder:
    def __init__(self, database_path="databases/lightning_fast_db.json"):
        self.database_path = database_path
        self.embeddings = []
        self.metadata = []
        self.processed_images = set()
        self.config = {
            "model": "ArcFace",
            "embedding_dim": 512,
            "enforce_detection": False
        }
        
        # Load existing database if it exists
        self.load_existing_database()
    
    def load_existing_database(self):
        """Load existing database to avoid reprocessing images"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r') as f:
                    data = json.load(f)
                
                self.embeddings = data.get('embeddings', [])
                self.metadata = data.get('metadata', [])
                
                # Track processed images to avoid duplicates
                for meta in self.metadata:
                    self.processed_images.add(meta['image_path'])
                
                print(f"✅ Loaded existing database: {len(self.embeddings)} faces")
            except Exception as e:
                print(f"⚠️ Could not load existing database: {e}")
                self.embeddings = []
                self.metadata = []
                self.processed_images = set()
    
    def extract_person_name(self, image_path):
        """Extract person name from image path"""
        filename = os.path.basename(image_path)
        
        # Handle formats like "Person Name_001.jpg" or "Person Name (1).jpg"
        if '_' in filename:
            person = filename.split('_')[0]
        elif '(' in filename:
            person = filename.split('(')[0].strip()
        else:
            # Use parent folder name
            person = os.path.basename(os.path.dirname(image_path))
        
        return person.replace('-', ' ').replace('_', ' ').strip()
    
    def get_face_embedding(self, image_path):
        """Extract face embedding from image"""
        try:
            result = DeepFace.represent(
                img_path=image_path,
                model_name=self.config["model"],
                enforce_detection=self.config["enforce_detection"]
            )
            
            if not result:
                return None
            
            embedding = np.array(result[0]['embedding'], dtype='float32')
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
        except Exception:
            return None
    
    def find_all_images(self, root_dirs=["Testing images"]):
        """Recursively find all image files"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = []
        
        for root_dir in root_dirs:
            if os.path.exists(root_dir):
                for root, dirs, files in os.walk(root_dir):
                    for file in files:
                        if Path(file).suffix.lower() in image_extensions:
                            image_path = os.path.join(root, file)
                            if image_path not in self.processed_images:
                                image_files.append(image_path)
        
        return image_files
    
    def process_new_images(self):
        """Process all new images and add to database"""
        new_images = self.find_all_images()
        
        if not new_images:
            print("✅ No new images to process")
            return
        
        print(f"🔄 Processing {len(new_images)} new images...")
        
        processed_count = 0
        failed_count = 0
        
        for i, image_path in enumerate(new_images):
            try:
                # Extract embedding
                embedding = self.get_face_embedding(image_path)
                
                if embedding is not None:
                    # Extract person name
                    person_name = self.extract_person_name(image_path)
                    
                    # Create metadata
                    metadata = {
                        "person": person_name,
                        "image_path": image_path,
                        "added_time": time.time()
                    }
                    
                    # Add to database
                    self.embeddings.append(embedding.tolist())
                    self.metadata.append(metadata)
                    self.processed_images.add(image_path)
                    
                    processed_count += 1
                    
                    # Progress update
                    if (i + 1) % 100 == 0:
                        print(f"⚡ {i + 1}/{len(new_images)} processed ({processed_count} successful)")
                
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                continue
        
        print(f"✅ Processing complete!")
        print(f"📊 New faces added: {processed_count}")
        print(f"❌ Failed images: {failed_count}")
        print(f"🎯 Total faces in database: {len(self.embeddings)}")
    
    def save_database(self):
        """Save the updated database"""
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        database_data = {
            "config": self.config,
            "embeddings": self.embeddings,
            "metadata": self.metadata,
            "total_faces": len(self.embeddings),
            "unique_persons": len(set(meta["person"] for meta in self.metadata)),
            "last_updated": time.time()
        }
        
        with open(self.database_path, 'w') as f:
            json.dump(database_data, f, indent=2)
        
        print(f"💾 Database saved: {self.database_path}")
        print(f"📁 File size: {os.path.getsize(self.database_path) / (1024*1024):.1f} MB")

def main():
    """Main function"""
    print("🚀 Professional Database Builder")
    print("=" * 50)
    
    builder = DatabaseBuilder()
    builder.process_new_images()
    builder.save_database()
    
    print("\n🎉 Database build complete!")
    print("   Run the Lightning Fast API to use the updated database.")

if __name__ == "__main__":
    main()
