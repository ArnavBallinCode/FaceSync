#!/usr/bin/env python3
"""
Lightning Fast Face Matcher API
Ultra-fast, minimal face matching with 7000 faces pre-loaded

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

import os
import time
import json
from pathlib import Path
from database_builders.database_builder import DatabaseBuilder

class AutoSync:
    def __init__(self):
        self.watch_dir = "Testing images"
        self.db_path = "databases/lightning_fast_db.json"
        self.last_check = 0
        
    def get_image_count(self):
        """Count all images in the Testing images directory"""
        if not os.path.exists(self.watch_dir):
            return 0
            
        count = 0
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        for root, dirs, files in os.walk(self.watch_dir):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    count += 1
        return count
    
    def get_db_image_count(self):
        """Get the number of images currently in the database"""
        if not os.path.exists(self.db_path):
            return 0
            
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            return data.get('total_faces', 0)
        except:
            return 0
    
    def check_for_updates(self):
        """Check if new images have been added"""
        current_image_count = self.get_image_count()
        db_image_count = self.get_db_image_count()
        
        print(f"📊 Images in folder: {current_image_count}")
        print(f"📊 Images in database: {db_image_count}")
        
        if current_image_count > db_image_count:
            print(f"🆕 Found {current_image_count - db_image_count} new images!")
            return True
        else:
            print("✅ Database is up to date")
            return False
    
    def rebuild_database(self):
        """Rebuild the database with new images"""
        print("🔄 Rebuilding database for perfect consistency...")
        print("=" * 60)
        
        builder = DatabaseBuilder()
        builder.verify_consistency()
        builder.process_new_images()
        builder.save_database()
        
        print("=" * 60)
        print("✅ Database rebuild complete!")
        print("🎯 Lightning Fast API now has 100% consistent results")
    
    def run_once(self):
        """Run a single check and update if needed"""
        print("🔍 Auto-Sync: Checking for new images...")
        
        if self.check_for_updates():
            self.rebuild_database()
            return True
        return False
    
    def run_continuous(self, interval=60):
        """Run continuous monitoring"""
        print(f"👁️  Auto-Sync: Monitoring '{self.watch_dir}' every {interval} seconds")
        print("   Press Ctrl+C to stop")
        
        try:
            while True:
                if self.check_for_updates():
                    self.rebuild_database()
                
                print(f"💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Auto-Sync stopped by user")

if __name__ == "__main__":
    import sys
    
    sync = AutoSync()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        sync.run_continuous()
    else:
        print("🚀 Auto-Sync Script")
        print("⚖️  Copyright (c) 2025 Arnav Angarkar. All rights reserved.")
        print("=" * 60)
        
        updated = sync.run_once()
        
        if updated:
            print("\n💡 Tip: Restart Lightning Fast API to load the updated database")
        else:
            print("\n💡 Tip: Add images to 'Testing images/' and run this script again")
        
        print("\n🔄 For continuous monitoring, run: python auto_sync.py --continuous")
