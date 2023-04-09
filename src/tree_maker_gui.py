import os
import json
import base64
import zlib
import mimetypes
import tkinter as tk
from tkinter import ttk, font, filedialog


def read_file_content(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    mode = 'r' if mime_type and mime_type.startswith("text") else 'rb'
    
    with open(file_path, mode) as f:
        content = f.read()

    return content if mode == 'r' else base64.b64encode(content).decode("utf-8")


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
        tree["children"].append(generate_tree(element_path) if os.path.isdir(element_path) else {
            "type": "file",
            "name": element,
            "content": compress_content(read_file_content(element_path))
        })

    return tree


def save_tree_json(tree, output_file):
    with open(output_file, "w") as f:
        json.dump(tree, f, indent=2)


def create_tree_from_json(tree, path):
    new_path = os.path.join(path, tree["name"])
    if tree["type"] == "directory":
        os.makedirs(new_path, exist_ok=True)
        for child in tree["children"]:
            create_tree_from_json(child, new_path)
    else:
        mime_type, _ = mimetypes.guess_type(tree["name"])
        content = decompress_content(tree["content"])
        mode = 'w' if mime_type and mime_type.startswith("text") else 'wb'
        
        with open(new_path, mode) as f:
            f.write(content if mode == 'w' else base64.b64decode(content.encode("utf-8")))


def gui():
    def update_execute_button_text(event):
        selected_tab = tab_control.tab(tab_control.select(), "text")
        if selected_tab == "Generate JSON":
            execute_button.config(text="GENERATE")
        elif selected_tab == "Create Tree":
            execute_button.config(text="CREATE")

    def browse_folder():
        folder_path.set(filedialog.askdirectory())

    def browse_json_file():
        json_file_path.set(filedialog.askopenfilename(filetypes=[("JSON files", "*.json")]))

    def execute():
        mode = tab_control.tab(tab_control.select(), "text")
        folder_path_val = folder_path.get()
        json_file_path_val = json_file_path.get()

        if mode == "Generate JSON" and folder_path_val:
            output_file = os.path.basename(os.path.abspath(folder_path_val)) + ".json"
            result_label.config(text="Generating JSON file...")
            save_tree_json(generate_tree(folder_path_val), output_file)
            result_label.config(text="Done! Generated JSON file: " + output_file)
        elif mode == "Create Tree" and json_file_path_val:
            with open(json_file_path_val, "r") as f:
                tree = json.load(f)

            output_folder_path = os.path.splitext(json_file_path_val)[0]
            result_label.config(text="Creating files and folders from JSON...")
            create_tree_from_json(tree, output_folder_path)
            result_label.config(text="Done! Created files and folders from JSON.")
        else:
            result_label.config(text="Please select a path to proceed.")

    root = tk.Tk()
    root.title("Tree Maker")
    root.resizable(False, False)
    root.geometry("700x200")

    tab_control = ttk.Notebook(root)
    generate_tab, create_tab = ttk.Frame(tab_control), ttk.Frame(tab_control)

    tab_control.add(generate_tab, text="Generate JSON")
    tab_control.add(create_tab, text="Create Tree")
    tab_control.grid(row=0, column=0, padx=10, pady=10)

    tab_control.bind("<<NotebookTabChanged>>", update_execute_button_text)

    folder_path, json_file_path = tk.StringVar(), tk.StringVar()

    folder_path_entry = tk.Entry(generate_tab, width=50, textvariable=folder_path)
    folder_path_entry.grid(row=0, column=0, padx=10, pady=10)

    browse_folder_button = tk.Button(generate_tab, text="Browse Folder", command=browse_folder)
    browse_folder_button.grid(row=0, column=1, padx=10, pady=10)

    json_file_entry = tk.Entry(create_tab, width=50, textvariable=json_file_path)
    json_file_entry.grid(row=0, column=0, padx=10, pady=10)

    browse_json_button = tk.Button(create_tab, text="Browse JSON", command=browse_json_file)
    browse_json_button.grid(row=0, column=1, padx=10, pady=10)

    execute_button_font = font.Font(size=15)
    execute_button_font.configure(weight="bold")
    execute_button = tk.Button(root, text="Generate", command=execute, font=execute_button_font)
    execute_button.config(width=10, height=1)
    execute_button.grid(row=1, column=0, padx=10, pady=0)

    result_label = tk.Label(root, text="")
    result_label.grid(row=2, column=0, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    gui()

