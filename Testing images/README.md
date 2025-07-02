# DeepFace ArcFace Recognition System

A high-accuracy, production-ready face recognition API and batch processing system built with FastAPI, ArcFace, DeepFace, and FAISS.

---

## Overview
This project provides a scalable, proprietary face recognition backend for both single and batch image processing. It is designed for high performance, reliability, and extensibility in real-world deployments.

---

## Key Features
- **FastAPI**: Modern, async Python web framework for robust APIs
- **ArcFace (via DeepFace)**: State-of-the-art face embedding (512-dim)
- **FAISS**: High-speed similarity search for large face databases
- **Batch & Single Upload**: Efficient endpoints for both use cases
- **Automated Scripts**: Tools for flattening image directories and batch uploading
- **Docker-ready**: Easy deployment and scaling
- **Proprietary License**: Strong legal protection and authorship

---

## Technologies Used
- Python 3.8+
- FastAPI
- DeepFace (ArcFace backend)
- FAISS
- NumPy
- Pillow
- Uvicorn
- Docker (optional)

---

## System Architecture (Mermaid.js)

```
flowchart TD
  AddFace[User uploads image(s)] --> API1[FastAPI receives image(s)]
  API1 --> Embedding1[ArcFace creates 512-dim embedding]
  Embedding1 --> Store1[Store embedding + metadata in memory]
  Store1 --> Faiss1[Add embedding to FAISS index]
  Store1 --> Save1[Save to arcface_database.json]

  MatchFace[User uploads image to match_face] --> API2[FastAPI receives image]
  API2 --> Embedding2[ArcFace creates 512-dim embedding]
  Embedding2 --> Query1[Query embedding]
  Query1 --> Faiss1
  Faiss1 --> Compare1[FAISS compares to all stored embeddings]
  Compare1 --> Result1[Return best match and confidence]
```

> Paste this diagram into [mermaid.live](https://mermaid.live/) or any Mermaid.js compatible tool to visualize the system flow.

---

## Usage
- Place your test images in the `Testing images/` folder.
- Use the provided scripts for batch upload and directory flattening.
- Run the FastAPI server for API access.

---

## License

```
Copyright (c) 2025 Arnav Angarkar. All rights reserved.

PROPRIETARY AND CONFIDENTIAL
This software and its documentation are proprietary to Arnav Angarkar.
No part of this software may be copied, reproduced, distributed, transmitted,
transcribed, stored in a retrieval system, or translated into any human or
computer language, in any form or by any means, electronic, mechanical,
magnetic, optical, chemical, manual, or otherwise, without the express
written permission of Arnav Angarkar.

Unauthorized copying, distribution, or use of this software is strictly
prohibited and may result in severe civil and criminal penalties.
```

---

## Folder: Testing Images

This folder contains all images used for testing and benchmarking the APIs and database builders.

- `Faces/`: International celebrity faces
- `Indian_faces/`: Indian celebrity faces
- `trainset/`: Additional training/test images

You can add your own images here for custom testing.
