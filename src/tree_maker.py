"""
Author: @flowese
Date: 2023-04-09

Creates a JSON file with the tree structure of the folder or creates folders and files from a JSON file.

Usage:  python tree_maker.py generate (-g) <folder_path>
        python tree_maker.py create (-c) <input_file.json>
"""

import os
import sys
import json
import base64
import mimetypes
import zlib

def read_file_content(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type and mime_type.startswith("text"):
        with open(file_path, "r") as f:
            content = f.read()
    else:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
    return content

def compress_content(content):
    return base64.b64encode(zlib.compress(content.encode("utf-8"))).decode("utf-8")

def decompress_content(content):
    return zlib.decompress(base64.b64decode(content.encode("utf-8"))).decode("utf-8")

def generate_tree(path):
    if not os.path.exists(path):
        return None

    tree = {"type": "directory", "name": os.path.basename(path), "children": []}

    for element in sorted(os.listdir(path)):
        element_path = os.path.join(path, element)

        if os.path.isdir(element_path):
            tree["children"].append(generate_tree(element_path))
        else:
            tree["children"].append({
                "type": "file",
                "name": element,
                "content": compress_content(read_file_content(element_path))
            })

    return tree

def save_tree_json(tree, output_file):
    with open(output_file, "w") as f:
        json.dump(tree, f, indent=2)

def create_tree_from_json(tree, path):
    if tree["type"] == "directory":
        os.makedirs(os.path.join(path, tree["name"]), exist_ok=True)

        for child in tree["children"]:
            create_tree_from_json(child, os.path.join(path, tree["name"]))
    elif tree["type"] == "file":
        mime_type, _ = mimetypes.guess_type(tree["name"])

        content = decompress_content(tree["content"])

        if mime_type and mime_type.startswith("text"):
            with open(os.path.join(path, tree["name"]), "w") as f:
                f.write(content)
        else:
            with open(os.path.join(path, tree["name"]), "wb") as f:
                f.write(base64.b64decode(content.encode("utf-8")))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python tree_maker.py generate (-g) <folder_path>")
        print("       python tree_maker.py create (-c) <input_file.json>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode in ("generate", "-g"):
        if len(sys.argv) != 3:
            print("Usage: python tree_maker.py generate (-g) <folder_path>")
            sys.exit(1)

        folder_path = sys.argv[2]
        output_file = os.path.basename(os.path.abspath(folder_path)) + ".json"
        
        print("Generating JSON file...")
        tree = generate_tree(folder_path)
        print("Saving JSON file...")
        save_tree_json(tree, output_file)
        print("Done!")

    elif mode in ("create", "-c"):
        if len(sys.argv) != 3:
            print("Usage: python tree_maker.py create (-c) <input_file.json>")
            sys.exit(1)

        input_file = sys.argv[2]

        with open(input_file, "r") as f:
            tree = json.load(f)

        output_folder_path = os.path.splitext(input_file)[0]
        print("Creating files and folders...")
        create_tree_from_json(tree, output_folder_path)
        print("Done!")
    else:
        print("Invalid mode. Use 'generate' (-g) or 'create' (-c)")
        sys.exit(1)
