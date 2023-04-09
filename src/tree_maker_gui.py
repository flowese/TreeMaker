import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
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

def gui():
    def browse_folder():
        folder_path = filedialog.askdirectory()
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)

    def browse_json_file():
        json_file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        json_file_entry.delete(0, tk.END)
        json_file_entry.insert(0, json_file_path)

    def execute():
        mode = tab_control.tab(tab_control.select(), "text")

        if mode == "Generate JSON":
            folder_path = folder_path_entry.get()
            if folder_path:
                output_file = os.path.basename(os.path.abspath(folder_path)) + ".json"
                tree = generate_tree(folder_path)
                result_label.config(text="Generating JSON file...")
                save_tree_json(tree, output_file)
                result_label.config(text="Done! Generated JSON file: " + output_file)
            else:
                result_label.config(text="Please select a folder to generate JSON file.")
        elif mode == "Create Tree":
            input_file = json_file_entry.get()
            if input_file:
                with open(input_file, "r") as f:
                    tree = json.load(f)

                output_folder_path = os.path.splitext(input_file)[0]
                result_label.config(text="Creating files and folders from JSON...")
                create_tree_from_json(tree, output_folder_path)
                result_label.config(text="Done! Created files and folders from JSON.")
            else:
                result_label.config(text="Please select a JSON file to create files and folders.")


    root = tk.Tk()
    root.title("Tree Maker")

    tab_control = ttk.Notebook(root)
    generate_tab = ttk.Frame(tab_control)
    create_tab = ttk.Frame(tab_control)

    tab_control.add(generate_tab, text="Generate JSON")
    tab_control.add(create_tab, text="Create Tree")
    tab_control.grid(row=0, column=0, padx=10, pady=10)

    folder_path_entry = tk.Entry(generate_tab, width=50)
    folder_path_entry.grid(row=0, column=0, padx=10, pady=10)

    browse_folder_button = tk.Button(generate_tab, text="Browse Folder", command=browse_folder)
    browse_folder_button.grid(row=0, column=1, padx=10, pady=10)

    json_file_entry = tk.Entry(create_tab, width=50)
    json_file_entry.grid(row=0, column=0, padx=10, pady=10)

    browse_json_button = tk.Button(create_tab, text="Browse JSON", command=browse_json_file)
    browse_json_button.grid(row=0, column=1, padx=10, pady=10)

    execute_button = tk.Button(root, text="Execute", command=execute)
    execute_button.grid(row=1, column=0, padx=10, pady=10)

    result_label = tk.Label(root, text="")
    result_label.grid(row=2, column=0, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    gui()