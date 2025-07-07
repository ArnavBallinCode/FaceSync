# Windows Setup Guide for DeepFace ArcFace API

This guide will help you get the DeepFace ArcFace API running on Windows.

## 1. Install Python 3.10 (Required)
- Download Python 3.10 from the official site: https://www.python.org/downloads/release/python-31011/
- Run the installer. Make sure to check **Add Python to PATH** during installation.

## 2. Create a Python 3.10 Virtual Environment
Open Command Prompt in the project directory and run:
```cmd
"C:\Program Files\Python310\python.exe" -m venv venv310
```

## 3. Activate the Virtual Environment
```cmd
venv310\Scripts\activate
```

## 4. Fix SSL Certificate Issues (if you get SSL errors)
Run this command:
```cmd
"C:\Program Files\Python310\python.exe" "C:\Program Files\Python310\Scripts\InstallCertificates.py"
```

## 5. Install Requirements (with extra timeout for large packages)
```cmd
venv310\Scripts\pip.exe install --default-timeout=600 -r requirements.txt
```

## 6. Run the API Server
```cmd
venv310\Scripts\python.exe api/main_arcface2.py
```

- The API will be available at: http://localhost:8002
- The interactive docs: http://localhost:8002/docs
- The UI (HTML, CSS, JS): http://localhost:8002/ui/index.html (or upload.html, etc.)

## 7. Troubleshooting
- If you see errors about missing packages, repeat step 5.
- If you see errors about DeepFace, make sure you are using Python 3.10 and not a newer version.
- If you see SSL errors, repeat step 4.

---

**This branch is for Windows compatibility.**
