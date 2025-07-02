#!/usr/bin/env python3
"""
Consistency Test Script
Verifies that the same image gets 100% confidence between database and API

Copyright (c) 2025 Arnav Angarkar. All rights reserved.
Author: Arnav Angarkar

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, distribution, or use prohibited.
"""

import requests
import os
import json
from pathlib import Path

def test_consistency():
    """Test that the same image gets 100% confidence"""
    
    print("🧪 Testing 100% Consistency Between Database and Lightning Fast API")
    print("=" * 70)
    
    # Check if Lightning Fast API is running
    try:
        response = requests.get("http://127.0.0.1:8001/")
        if response.status_code != 200:
            print("❌ Lightning Fast API is not running on port 8001")
            print("   Start it with: python api/api_lightning_fast.py")
            return
    except:
        print("❌ Cannot connect to Lightning Fast API on port 8001")
        print("   Start it with: python api/api_lightning_fast.py")
        return
    
    # Find a test image
    test_image = None
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    if os.path.exists("Testing images"):
        for root, dirs, files in os.walk("Testing images"):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    test_image = os.path.join(root, file)
                    break
            if test_image:
                break
    
    if not test_image:
        print("❌ No test images found in 'Testing images/' folder")
        print("   Add some images and rebuild the database first")
        return
    
    print(f"🖼️  Using test image: {test_image}")
    
    # Test the API
    try:
        with open(test_image, 'rb') as f:
            files = {'file': f}
            response = requests.post("http://127.0.0.1:8001/search", files=files)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if matches:
                best_match = matches[0]
                confidence = best_match.get('confidence', 0)
                
                print(f"🎯 Best match confidence: {confidence}%")
                print(f"🎯 Distance: {best_match.get('distance', 'N/A')}")
                print(f"🎯 Person: {best_match.get('person', 'Unknown')}")
                
                if confidence >= 99.0:
                    print("✅ EXCELLENT: Near-perfect consistency achieved!")
                elif confidence >= 95.0:
                    print("✅ GOOD: High consistency achieved!")
                elif confidence >= 90.0:
                    print("⚠️  MODERATE: Some variation present")
                else:
                    print("❌ LOW: Significant variation - check parameters")
                
                # Show debug info
                debug_info = data.get('debug_info', {})
                if debug_info:
                    print(f"\n🔍 Debug Info:")
                    print(f"   Top 3 raw scores: {debug_info.get('top_3_raw_scores', [])}")
                    print(f"   Query embedding norm: {debug_info.get('query_embedding_norm', 'N/A')}")
                
            else:
                print("❌ No matches found - check if image is in database")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n💡 For 100% consistency:")
    print("   1. Ensure database was built with the same image")
    print("   2. Use identical DeepFace parameters")
    print("   3. Same detection and normalization settings")

if __name__ == "__main__":
    test_consistency()
