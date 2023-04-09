# Tree Maker Tool

This project is a Python script that generates a JSON file with the tree structure of a folder or creates folders and files from a JSON file. It works with all types of directories and files. 

Media and binary files are base64 encoded in the JSON file to ensure correct generation of directories from the JSON.

The project does not have any external dependencies and uses only the libraries included by default in Python.

## Just download the binaries for your system:

###
[Download Windows (x86_64)](https://github.com/flowese/tree_maker/releases/download/tree_maker_v1/tree_maker_win_v1.exe)
###
[Download MacOSX (x86_64)](https://github.com/flowese/tree_maker/releases/download/tree_maker_v1/tree_maker_osx_v1)
###
[Download Linux (x86_64)](https://github.com/flowese/tree_maker/releases/download/tree_maker_v1/tree_maker_lin_v1)

## Usage
### Open binary on terminal or cmd:
(Example for Windows) 

```bash
tree_maker.exe -g <folder_path>
```

## For Devs. Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/flowese/tree_maker.git
    ```
2. Navigate to the project directory:

    ```sh
    cd tree_maker
    ```

## Usage Dev.

To generate a JSON file with the tree structure of a folder, run the following command:
```sh
python tree_maker.py generate <folder_path>
```

To create folders and files from a JSON file, run the following command:
```sh
python tree_maker.py create <input_file.json>
```

## Examples
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
