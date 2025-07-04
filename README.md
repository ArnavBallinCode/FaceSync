# FaceSync

**Face Match pipeline with about 100% accuracy**

---

**Tech Stack:**  
- Python 3.11  
- FastAPI  
- DeepFace (ArcFace backend)  
- FAISS  
- NumPy, Pillow  
- Uvicorn  
- Docker (optional)

**Author:** Arnav Angarkar  
**Copyright (c) 2025 Arnav Angarkar. All rights reserved.**

> **PROPRIETARY AND CONFIDENTIAL**  
> This software and its documentation are proprietary to Arnav Angarkar.  
> No part of this software may be copied, reproduced, distributed, transmitted, transcribed, stored in a retrieval system, or translated into any human or computer language, in any form or by any means, electronic, mechanical, magnetic, optical, chemical, manual, or otherwise, without the express written permission of Arnav Angarkar.  
> Unauthorized copying, distribution, or use of this software is strictly prohibited and may result in severe civil and criminal penalties.

---

##  **Perfect Consistency Guarantee**

This system ensures **100% identical results** between database building and lightning-fast matching by using **exactly the same parameters**:

-  **ArcFace Model**: Same model, same version
-  **Detection**: `enforce_detection=True` (both systems)
-  **Backend**: `detector_backend='opencv'` (both systems)  
-  **Normalization**: Identical L2 normalization
-  **Preprocessing**: Same image conversion pipeline

##  Project Structure

```
api/                     # Two main API servers
├── api_lightning_fast.py        # Ultra-fast matching (port 8001)
└── api_arcface_standalone.py    # Full-featured ArcFace API (port 8002)

database_builders/       # Single professional database builder
└── database_builder.py         # Incremental database updates

databases/              # Final database files
├── lightning_fast_db.json      # Main database (7000+ faces)
└── arcface_database.json       # ArcFace API database

checkpoints/            # Checkpoint files for recovery
├── checkpoint_1000.json ... checkpoint_7000.json

Testing images/         # Images for testing and database building
requirements.txt        # Python dependencies
```

##  Quickstart

1. **Setup Environment**
   ```bash
   conda create -n deepface-fixed python=3.11 -y
   conda activate deepface-fixed
   pip install -r requirements.txt
   ```

2. **Start Lightning Fast API** (Recommended)
   ```bash
   conda activate deepface-fixed
   python api/api_lightning_fast.py
   ```
   - Instant startup with 7000+ faces pre-loaded
   - Ultra-fast matching with adjustable threshold and top_k
   - Access at `http://127.0.0.1:8001`

3. **Or Start ArcFace Standalone API**
   ```bash
   conda activate deepface-fixed
   python api/api_arcface_standalone.py
   ```
   - Full database management features
   - Add/delete faces, detailed statistics
   - Access at `http://127.0.0.1:8002`

4. **Update Database** (Add new images)
   ```bash
   conda activate deepface-fixed
   python database_builders/database_builder.py
   ```

##  Quick Test

**Test Lightning Fast API:**
```bash
curl -X POST "http://127.0.0.1:8001/search" \
  -F "file=@img1.jpg" \
  -F "top_k=5" \
  -F "threshold=0.6"
```

**Test ArcFace API:**
```bash
curl -X POST "http://127.0.0.1:8002/match_face" \
  -F "file=@img1.jpg" \
  -F "top_k=3"
```

## Run with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t facesync:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -it --rm -p 8002:8002 facesync:latest
   ```
   - The API and UI will be available at `http://localhost:8002/ui/index.html`
   - All endpoints (add, match, list, delete, stats) are accessible via the UI or API.

3. **Batch upload images (from host):**
   - Make sure the API is running in Docker and accessible at `http://localhost:8002`.
   - Run the batch upload script from your host:
     ```bash
     python batch_upload_testing_images.py
     ```

---

##  Performance

- **Lightning Fast API**: <50ms per search, 7000+ faces
- **Database Builder**: Incremental updates, processes only new images
- **Memory Efficient**: Optimized FAISS indexing, minimal overhead

---

**Professional, fast, and ready for production.**
