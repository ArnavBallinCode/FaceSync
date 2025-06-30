# API Servers

This folder contains the two main face recognition APIs:

- `api_lightning_fast.py`: Ultra-fast face matching API with 7000+ pre-loaded faces. Minimal overhead, maximum speed.
- `api_arcface_standalone.py`: Professional ArcFace API for high-accuracy face recognition with database management.

## Usage

**Lightning Fast API (Port 8001):**
```bash
conda activate deepface-fixed
python api/api_lightning_fast.py
```

**ArcFace Standalone API (Port 8002):**
```bash
conda activate deepface-fixed
python api/api_arcface_standalone.py
```

## Endpoints

**Lightning Fast API:**
- `GET /` - Status and statistics
- `POST /search` - Ultra-fast face matching with adjustable top_k and threshold

**ArcFace Standalone API:**
- `GET /` - API information and endpoints
- `POST /add_face` - Add new face to database
- `POST /match_face` - Match face against database
- `GET /list_faces` - List all faces
- `DELETE /delete_face/{id}` - Delete face
- `GET /stats` - Detailed statistics
