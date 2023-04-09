import os
import json
import base64
import zlib
import mimetypes
import tkinter as tk
from tkinter import ttk, font, filedialog


class TreeMaker:
    @staticmethod
    def read_file_content(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        is_text = mime_type and mime_type.startswith("text")

        with open(file_path, 'rb') as f:
            content = f.read()

        if is_text:
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                pass

        return base64.b64encode(content).decode("utf-8")

    @staticmethod
    def compress_content(content):
        return base64.b64encode(zlib.compress(content.encode("utf-8"))).decode("utf-8")

    @staticmethod
    def decompress_content(content):
        return zlib.decompress(base64.b64decode(content.encode("utf-8"))).decode("utf-8")

    @staticmethod
    def generate_tree(path):
        if not os.path.exists(path):
            return None

        tree = {"type": "directory", "name": os.path.basename(path), "children": []}
        for element in sorted(os.listdir(path)):
            element_path = os.path.join(path, element)
            tree["children"].append(TreeMaker.generate_tree(element_path) if os.path.isdir(element_path) else {
                "type": "file",
                "name": element,
                "content": TreeMaker.compress_content(TreeMaker.read_file_content(element_path))
            })

        return tree

    @staticmethod
    def save_tree_json(tree, output_file):
        with open(output_file, "w") as f:
            json.dump(tree, f, indent=2)

    @staticmethod
    def create_tree_from_json(tree, path):
        new_path = os.path.join(path, tree["name"])
        if tree["type"] == "directory":
            os.makedirs(new_path, exist_ok=True)
            for child in tree["children"]:
                TreeMaker.create_tree_from_json(child, new_path)
        else:
            mime_type, _ = mimetypes.guess_type(tree["name"])
            content = TreeMaker.decompress_content(tree["content"])
            mode = 'w' if mime_type and mime_type.startswith("text") else 'wb'

            with open(new_path, mode) as f:
                f.write(content if mode == 'w' else base64.b64decode(content.encode("utf-8")))


class TreeMakerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tree Maker")
        self.root.resizable(False, False)
        self.root.geometry("700x200")

        self.init_ui()

    def init_ui(self):
        self.folder_path = tk.StringVar()
        self.json_file_path = tk.StringVar()

        self.tab_control = ttk.Notebook(self.root)
        self.generate_tab, self.create_tab = ttk.Frame(self.tab_control), ttk.Frame(self.tab_control)

        self.tab_control.add(self.generate_tab, text="Generate JSON")
        self.tab_control.add(self.create_tab, text="Create Tree")
        self.tab_control.grid(row=0, column=0, padx=10, pady=10)

        self.tab_control.bind("<<NotebookTabChanged>>", self.update_execute_button_text)

        self.folder_path_entry = tk.Entry(self.generate_tab, width=50, textvariable=self.folder_path)
        self.folder_path_entry.grid(row=0, column=0, padx=10, pady=10)

        self.browse_folder_button = tk.Button(self.generate_tab, text="Browse Folder", command=self.browse_folder)
        self.browse_folder_button.grid(row=0, column=1, padx=10, pady=10)

        self.json_file_entry = tk.Entry(self.create_tab, width=50, textvariable=self.json_file_path)
        self.json_file_entry.grid(row=0, column=0, padx=10, pady=10)

        self.browse_json_button = tk.Button(self.create_tab, text="Browse JSON", command=self.browse_json_file)
        self.browse_json_button.grid(row=0, column=1, padx=10, pady=10)

        self.execute_button_font = font.Font(size=15)
        self.execute_button_font.configure(weight="bold")
        self.execute_button = tk.Button(self.root, text="Generate", command=self.execute, font=self.execute_button_font)
        self.execute_button.config(width=10, height=1)
        self.execute_button.grid(row=1, column=0, padx=10, pady=0)

        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=2, column=0, padx=10, pady=10)

    def update_execute_button_text(self, event):
        selected_tab = self.tab_control.tab(self.tab_control.select(), "text")
        if selected_tab == "Generate JSON":
            self.execute_button.config(text="GENERATE")
        elif selected_tab == "Create Tree":
            self.execute_button.config(text="CREATE")

    def browse_folder(self):
        self.folder_path.set(filedialog.askdirectory())

    def browse_json_file(self):
        self.json_file_path.set(filedialog.askopenfilename(filetypes=[("JSON files", "*.json")]))

    def execute(self):
        mode = self.tab_control.tab(self.tab_control.select(), "text")
        folder_path_val = self.folder_path.get()
        json_file_path_val = self.json_file_path.get()

        if mode == "Generate JSON" and folder_path_val:
            output_file = os.path.basename(os.path.abspath(folder_path_val)) + ".json"
            self.result_label.config(text="Generating JSON file...")
            TreeMaker.save_tree_json(TreeMaker.generate_tree(folder_path_val), output_file)
            self.result_label.config(text="Done! Generated JSON file: " + output_file)
        elif mode == "Create Tree" and json_file_path_val:
            with open(json_file_path_val, "r") as f:
                tree = json.load(f)

            output_folder_path = os.path.splitext(json_file_path_val)[0]
            self.result_label.config(text="Creating files and folders from JSON...")
            TreeMaker.create_tree_from_json(tree, output_folder_path)
            self.result_label.config(text="Done! Created files and folders from JSON.")
        else:
            self.result_label.config(text="Please select a path to proceed.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TreeMakerGUI()
    app.run()
