#!/usr/bin/env python3
"""
copies a file from /tmp to the decommissioned vms share using python's shutil.copy2.
returns a json dict with status and message.

tsvetelin.maslarski-ext@ldc.com
"""
import os
import json
import shutil

filename = os.environ.get("FILENAME")
dest_path = os.environ.get("DEST_PATH")

src_file = f"/tmp/{filename}"
dest_file = f"{dest_path}/{filename}"

def copy_file():
    try:
        shutil.copy2(src_file, dest_file)
        return json.dumps({
            'status': 'success',
            'message': f'copied {src_file} to {dest_file}'
        })
    except Exception as e:
        return json.dumps({
            'status': 'failed',
            'message': f'failed to copy {src_file} to {dest_file}. error: {e}'
        })

if __name__ == '__main__':
    print(copy_file())

