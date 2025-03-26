# Directory Tree Creator

A GUI application that generates directory structures from text-based tree representations. This tool lets you quickly create project scaffolding by converting a visual directory tree into actual files and folders.

![Directory Tree Creator Screenshot](screenshot.png)

## Features

- **Intuitive GUI Interface**: No command-line knowledge required
- **Multiple Input Formats**:
  - Simple indented format (with directories ending in `/`)
  - ASCII tree format (like the output from the `tree` command)
- **Comments Support**: Add comments to document your structure (after `#`)
- **Real-time Progress**: Visual feedback as files and directories are created
- **Permission Handling**: Graceful handling of permission issues with helpful error messages

## Installation

### Option 1: Download the Executable (Windows)

If you're on Windows, you can download the pre-built executable from the [Releases](https://github.com/yourusername/directory-tree-creator/releases) page.

### Option 2: Run from Source

1. Make sure you have Python 3.6+ installed
2. Clone this repository:
   ```
   git clone https://github.com/yourusername/directory-tree-creator.git
   cd directory-tree-creator
   ```
3. Run the application:
   ```
   python directory_tree_creator_gui.py
   ```

### Option 3: Build Your Own Executable

1. Install the requirements:
   ```
   pip install pyinstaller pillow
   ```
2. Run the build script:
   ```
   python build_exe.py
   ```
3. Find the executable in the `dist` folder

## Usage

1. Launch the application
2. Enter your directory structure in the text area using one of the supported formats
3. Select an output directory where the structure will be created
4. Click "Create Directory Structure"

### Input Format Examples

#### Indented Format

```
project/
    src/
        main.py
        utils.py
    docs/
        index.md
    README.md
```

#### ASCII Tree Format

```
project/
├── config.py                    # Application configuration settings
├── main.py                      # Application entry point
├── requirements.txt             # Project dependencies
├── README.md                    # Project documentation
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Service orchestration
├── .gitignore                   # Git ignore patterns
│
├── data/                        # Data directory
│   └── .gitkeep                 # Placeholder to keep directory in git
│
├── logs/                        # Log files directory
│   └── .gitkeep                 # Placeholder to keep directory in git
│
├── output/                      # Output files directory
│   └── .gitkeep                 # Placeholder to keep directory in git
│
├── scripts/                     # Utility scripts
│   └── setup_environment.py     # Environment setup script
│
├── services/                    # Service modules
│   ├── __init__.py              # Package initialization
│   ├── data_service.py          # Data loading/saving service
│   └── processing_service.py    # Data processing service
│
└── utils/                       # Utility modules
    ├── __init__.py              # Package initialization
    ├── error_handler.py         # Error handling utilities
    └── logger.py                # Logging configuration
```

## How It Works

The application parses the text-based tree representation and creates the corresponding files and directories in the selected output location. It detects the format automatically and provides real-time progress updates during creation.

## Project Structure

- `directory_tree_creator_gui.py`: Main application file with GUI implementation
- `build_exe.py`: Script to build the standalone executable
- `icons/`: Folder containing application icons
- `dist/`: Contains the built executable (after running build script)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and Tkinter
- Icon sources (if applicable)
- Inspired by the need for quick project scaffolding
