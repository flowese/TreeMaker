import json
import base64
import zlib
import mimetypes
import tkinter as tk
from tkinter import ttk, font, filedialog
import threading
from pathlib import Path
import argparse
import sys
import locale

def get_text(key):
    translations = {
        "en": {
            "select_folder": "Select folder:",
            "browse_folder": "Browse Folder",
            "select_json": "Select JSON file:",
            "browse_json": "Browse JSON",
            "generate_json": "Generate JSON",
            "create_tree": "Create Tree",
            "generating_json": "Generating JSON file...",
            "done_generated_json": "Done! Generated JSON file: ",
            "cancelled_json_generation": "Cancelled JSON file generation.",
            "please_select_folder": "Please select a folder to proceed.",
            "please_select_json": "Please select a JSON file to proceed.",
            "cancelled_folder_creation": "Cancelled folder creation.",
            "creating_files_folders": "Creating files and folders from JSON...",
            "done_created_files_folders": "Done! Created files and folders from JSON."
        },
        "es": {
            "select_folder": "Seleccionar carpeta:",
            "browse_folder": "Buscar carpeta",
            "select_json": "Seleccionar archivo JSON:",
            "browse_json": "Buscar JSON",
            "generate_json": "Generar JSON",
            "create_tree": "Crear árbol",
            "generating_json": "Generando archivo JSON...",
            "done_generated_json": "¡Listo! Archivo JSON generado: ",
            "cancelled_json_generation": "Se canceló la generación del archivo JSON.",
            "please_select_folder": "Por favor, seleccione una carpeta para continuar.",
            "please_select_json": "Por favor, seleccione un archivo JSON para continuar.",
            "cancelled_folder_creation": "Se canceló la creación de la carpeta.",
            "creating_files_folders": "Creando archivos y carpetas a partir de JSON...",
            "done_created_files_folders": "¡Listo! Se crearon archivos y carpetas a partir de JSON."
        }
    }

    lang = locale.getdefaultlocale()[0][:2]

    if lang in translations:
        return translations[lang].get(key, key)
    else:
        return translations["en"].get(key, key)


class TreeMaker:
    def read_file_content(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        is_text = mime_type and mime_type.startswith("text")

        with open(file_path, 'rb') as f:
            content = f.read()

        if is_text:
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                pass

        compressed_content = zlib.compress(content)
        return base64.b64encode(compressed_content).decode("utf-8")

    def decompress_content(self, content, is_text):
        if is_text:
            return content

        compressed_content = base64.b64decode(content.encode("utf-8"))
        return zlib.decompress(compressed_content)

    def generate_tree(self, path):
        if not path.exists():
            return None

        tree = {"type": "directory", "name": path.name, "children": []}
        for element in sorted(path.iterdir()):
            if element.is_dir():
                tree["children"].append(self.generate_tree(element))
            else:
                mime_type, _ = mimetypes.guess_type(element)
                is_text = mime_type and mime_type.startswith("text")
                tree["children"].append({
                    "type": "file",
                    "name": element.name,
                    "content": self.read_file_content(element),
                    "is_text": is_text
                })

        return tree

    def save_tree_json(self, tree, output_file):
        with open(output_file, "w") as f:
            json.dump(tree, f, indent=2)

    def create_tree_from_json(self, tree, path):
        new_path = Path(path) / tree["name"]
        if tree["type"] == "directory":
            new_path.mkdir(parents=True, exist_ok=True)
            for child in tree["children"]:
                self.create_tree_from_json(child, new_path)
        else:
            content = self.decompress_content(tree["content"], tree["is_text"])
            mode = 'w' if tree["is_text"] else 'wb'

            with open(new_path, mode) as f:
                f.write(content)


class GenerateTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.folder_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        folder_path_label = tk.Label(self, text=get_text("select_folder"))
        folder_path_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="e")

        folder_path_entry = tk.Entry(self, width=50, textvariable=self.folder_path)
        folder_path_entry.grid(row=0, column=1, padx=(10, 10), pady=10)

        browse_folder_button = tk.Button(self, text=get_text("browse_folder"), command=self.browse_folder)
        browse_folder_button.grid(row=0, column=2, padx=(0, 10), pady=10)

    def browse_folder(self):
        self.folder_path.set(filedialog.askdirectory())


class CreateTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.json_file_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        json_file_label = tk.Label(self, text=get_text("select_json"))
        json_file_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="e")

        json_file_entry = tk.Entry(self, width=50, textvariable=self.json_file_path)
        json_file_entry.grid(row=0, column=1, padx=(10, 10), pady=10)

        browse_json_button = tk.Button(self, text=get_text("browse_json"), command=self.browse_json_file)
        browse_json_button.grid(row=0, column=2, padx=(0, 10), pady=10)


    def browse_json_file(self):
        self.json_file_path.set(filedialog.askopenfilename(filetypes=[("JSON files", "*.json")]))


class TreeMakerCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Tree Maker - Create JSON files representing a directory tree and recreate the directory tree from JSON files.")
        subparsers = self.parser.add_subparsers(dest="command", required=True)

        generate_parser = subparsers.add_parser("generate", aliases=["-g"], help="Generate a JSON file representing a directory tree.")
        generate_parser.add_argument("folder_path", type=str, help="Path to the directory you want to represent in a JSON file.")

        create_parser = subparsers.add_parser("create", aliases=["-c"], help="Create a directory tree from a JSON file.")
        create_parser.add_argument("input_file", type=str, help="Path to the JSON file representing the directory tree.")

    def run(self):
        args = self.parser.parse_args()
        tree_maker = TreeMaker()

        if args.command == "generate" or args.command == "-g":
            folder_path = Path(args.folder_path)
            output_file = f"{folder_path.name}.json"
            tree_maker.save_tree_json(tree_maker.generate_tree(folder_path), output_file)
            print(f"Generated JSON file: {output_file}")

        elif args.command == "create" or args.command == "-c":
            with open(args.input_file, "r") as f:
                tree = json.load(f)

            output_folder_path = input("Enter the path where you want to create the directory tree: ")
            tree_maker.create_tree_from_json(tree, output_folder_path)
            print(f"Created files and folders from JSON in {output_folder_path}")



class TreeMakerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tree Maker")
        self.root.resizable(False, False)
        self.root.geometry("880x200")

        self.init_ui()

    def init_ui(self):
        self.tab_control = ttk.Notebook(self.root)
        self.generate_tab = GenerateTab(self.tab_control, self)
        self.create_tab = CreateTab(self.tab_control, self)

        self.tab_control.add(self.generate_tab, text=get_text("generate_json"))
        self.tab_control.add(self.create_tab, text=get_text("create_tree"))
        self.tab_control.grid(row=0, column=0, padx=10, pady=10)

        self.tab_control.bind("<<NotebookTabChanged>>", self.update_execute_button_text)

        self.execute_button_font = font.Font(size=15)
        self.execute_button_font.configure(weight="bold")
        self.execute_button = tk.Button(self.root, text="Generate", command=self.execute, font=self.execute_button_font)
        self.execute_button.config(width=10, height=1)
        self.execute_button.grid(row=1, column=0, padx=10, pady=(0, 10))  # Cambiar el valor de pady aquí

        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=2, column=0, padx=10, pady=(0, 10))

    def update_execute_button_text(self, event):
        selected_tab = self.tab_control.tab(self.tab_control.select(), "text")
        if selected_tab == get_text("generate_json"):
            self.execute_button.config(text=get_text("generate_json").upper())
        elif selected_tab == get_text("create_tree"):
            self.execute_button.config(text=get_text("create_tree").upper())


    def execute(self):
        def execute_thread():
            tree_maker = TreeMaker()  # Crear una instancia de TreeMaker
            selected_tab = self.tab_control.tab(self.tab_control.select(), "text")
            self.execute_button.config(state=tk.DISABLED)  # Deshabilitar el botón durante la ejecución

            selected_tab = self.tab_control.tab(self.tab_control.select(), "text")

            if selected_tab == "Generate JSON":
                folder_path_val = self.generate_tab.folder_path.get()

                if folder_path_val:
                    output_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
                    if output_file:
                        self.result_label.config(text=get_text("generating_json"))

                        folder_path = Path(folder_path_val)  # Convertir la cadena a un objeto Path
                        tree_maker.save_tree_json(tree_maker.generate_tree(folder_path), output_file)  # Cambio aquí
                        self.result_label.config(text=get_text("generated_json"))
                    else:
                        self.result_label.config(text=get_text("cancelled_json_generation"))

                else:
                    self.result_label.config(text=get_text("select_folder_to_proceed"))


            elif selected_tab == "Create Tree":
                json_file_path_val = self.create_tab.json_file_path.get()

                if json_file_path_val:
                    with open(json_file_path_val, "r") as f:
                        tree = json.load(f)

                    output_folder_path = filedialog.askdirectory()
                    if output_folder_path:
                        self.result_label.config(text="Creating files and folders from JSON...")
                        tree_maker.create_tree_from_json(tree, output_folder_path)
                        self.result_label.config(text="Done! Created files and folders from JSON.")
                    else:
                        self.result_label.config(text="Cancelled folder creation.")

                else:
                    self.result_label.config(text="Please select a JSON file to proceed.")

            self.execute_button.config(state=tk.NORMAL)  # Habilitar el botón al finalizar la ejecución

        # Crear y ejecutar un hilo para realizar la tarea sin bloquear la GUI
        execution_thread = threading.Thread(target=execute_thread)
        execution_thread.start()


    def run(self):
        self.root.mainloop()


def main():
    if len(sys.argv) > 1:  # Si hay argumentos en la línea de comandos, usar la interfaz de línea de comandos
        cli = TreeMakerCLI()
        cli.run()
    else:  # De lo contrario, usar la interfaz gráfica de usuario
        app = TreeMakerGUI()
        app.run()


if __name__ == "__main__":
    main()

