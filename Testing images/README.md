# Testing Images

This folder contains all images used for testing and benchmarking the APIs and database builders.

- `Faces/`: International celebrity faces
- `Indian_faces/`: Indian celebrity faces
- `trainset/`: Additional training/test images

You can add your own images here for custom testing.

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
