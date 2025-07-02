import os
import shutil

root_dir = "Testing images"

for subdir, dirs, files in os.walk(root_dir):
    # Skip the root itself
    if subdir == root_dir:
        continue
    for file in files:
        src = os.path.join(subdir, file)
        dst = os.path.join(root_dir, file)
        # If a file with the same name exists, rename to avoid overwrite
        if os.path.exists(dst):
            base, ext = os.path.splitext(file)
            i = 1
            while os.path.exists(os.path.join(root_dir, f"{base}_{i}{ext}")):
                i += 1
            dst = os.path.join(root_dir, f"{base}_{i}{ext}")
        shutil.move(src, dst)

print("All images moved to root of 'Testing images/'")
