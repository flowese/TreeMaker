# Tree Maker

This project is a Python script that generates a JSON file with the tree structure of a folder or creates folders and files from a JSON file. It works with all types of directories and files. 

Media and binary files are base64 encoded in the JSON file to ensure correct generation of directories from the JSON.

The project does not have any external dependencies and uses only the libraries included by default in Python.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/flowese/tree_maker.git
    ```
2. Navigate to the project directory:

    ```sh
    cd tree_maker
    ```

## Usage

To generate a JSON file with the tree structure of a folder, run the following command:
```sh
python tree_maker.py generate <folder_path>
```

To create folders and files from a JSON file, run the following command:
```sh
python tree_maker.py create <input_file.json>
```

##Examples
To generate a JSON file with the tree structure of the current directory, run the following command:
```sh
python tree_maker.py generate .
```

To create folders and files from a JSON file, run the following command:
```sh
python tree_maker.py create example.json
```

## Author

- [@flowese](https://github.com/flowese)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
