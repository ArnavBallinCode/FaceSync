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
