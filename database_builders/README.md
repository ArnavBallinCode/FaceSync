# Database Builder

Single, professional database builder for the Lightning Fast Face Recognition System.

## File

- `database_builder.py`: Recursively scans all image folders and adds new images to the lightning fast database. Supports incremental updates - only processes new images not already in the database.

## Usage

```bash
conda activate deepface-fixed
python database_builders/database_builder.py
```

## Features

- **Incremental Updates**: Only processes new images not already in the database
- **Recursive Scanning**: Finds images in any subfolder under "Testing images"
- **Professional Progress Tracking**: Shows processing progress and statistics
- **Error Handling**: Continues processing even if some images fail
- **Automatic Person Detection**: Extracts person names from file/folder structure

The builder will update the `databases/lightning_fast_db.json` file with any new faces found.
