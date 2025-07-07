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
import requests

API_URL = "http://localhost:8002/add_faces_multi"
IMAGES_DIR = "Testing images"
BATCH_SIZE = 999

# Get all image files in the directory (no subfolders)
all_files = [f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))]
total = len(all_files)
print(f"Found {total} images.")

for i in range(0, total, BATCH_SIZE):
    batch_files = all_files[i:i+BATCH_SIZE]
    files = [("files", (fname, open(os.path.join(IMAGES_DIR, fname), "rb"))) for fname in batch_files]
    print(f"Uploading batch {i//BATCH_SIZE + 1}: {len(batch_files)} images...")
    try:
        response = requests.post(API_URL, files=files)
        print(f"Batch {i//BATCH_SIZE + 1} response: {response.status_code}")
        try:
            print(response.json())
        except Exception:
            print(response.text)
    except Exception as e:
        print(f"Error uploading batch {i//BATCH_SIZE + 1}: {e}")
    finally:
        # Close all file handles
        for _, (_, f) in files:
            f.close()
print("All batches processed.")
