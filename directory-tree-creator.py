#!/usr/bin/env python3
"""
Directory Tree Creator GUI

This application creates a directory structure based on text-based tree representations.
It supports both indented format and ASCII tree format (like output from the 'tree' command).
"""

import os
import re
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox


def parse_indented_tree(tree_text):
    """
    Parse a simple indented text-based tree representation into a nested dictionary.
    
    Args:
        tree_text (str): The indented text representation of the directory tree
        
    Returns:
        dict: A nested dictionary representing the directory structure
    """
    lines = tree_text.strip().split('\n')
    root = {}
    path_stack = []
    indent_stack = [-1]
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Calculate the indentation level (number of spaces)
        indent = len(line) - len(line.lstrip())
        line = line.strip()
        
        # Determine if it's a directory or file
        is_dir = line.endswith('/')
        name = line[:-1] if is_dir else line
        
        # Validate name
        if not name or ('/' in name and not name.startswith('#')) or ('\\' in name and not name.startswith('#')):
            raise ValueError(f"Invalid name: '{name}'. Names cannot contain '/' or '\\'.")
        
        # Adjust the path stack based on indentation
        while indent <= indent_stack[-1]:
            indent_stack.pop()
            path_stack.pop()
        
        # Update the current path
        if not path_stack:
            # This is the root
            current = root
        else:
            # Navigate to the current position in the nested dict
            current = root
            for p in path_stack:
                if p not in current:
                    current[p] = {}
                current = current[p]
        
        # Add the new entry
        current[name] = {} if is_dir else None
        
        # Update stacks if this is a directory
        if is_dir:
            path_stack.append(name)
            indent_stack.append(indent)
    
    return root


def parse_ascii_tree(tree_text):
    """
    Parse an ASCII tree representation (like the one from 'tree' command)
    into a nested dictionary.
    
    Args:
        tree_text (str): The ASCII text representation of the directory tree
        
    Returns:
        dict: A nested dictionary representing the directory structure
    """
    lines = tree_text.strip().split('\n')
    root = {}
    
    if not lines:
        return root
    
    # First line is the root directory
    root_line = lines[0].strip()
    if root_line.endswith('/'):
        root_name = root_line[:-1]
    else:
        # If the root doesn't end with /, we'll create a fake root
        root_name = "root"
        lines.insert(0, root_name + "/")
    
    # Initialize structure
    structure = {root_name: {}}
    path_stack = [root_name]
    
    # Parse the rest of the lines
    for i in range(1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        
        # Extract path depth from the ASCII tree
        # We'll check for '│', '├', '└', and '─' characters
        depth = 0
        content_start = 0
        
        # Match ASCII tree characters to determine the depth
        match = re.search(r'[│├└](?:──|─)', line)
        if match:
            content_start = match.end()
            # Count path segments
            depth = line[:match.end()].count('│') + line[:match.end()].count('├') + line[:match.end()].count('└')
        
        # Extract the name and comment
        content = line[content_start:].strip()
        comment = ""
        
        # Check if there's a comment
        if '#' in content:
            parts = content.split('#', 1)
            content = parts[0].strip()
            comment = parts[1].strip()
        
        # Determine if it's a directory
        is_dir = content.endswith('/')
        name = content[:-1] if is_dir else content
        
        # Adjust the path stack based on depth
        while len(path_stack) > depth + 1:
            path_stack.pop()
        
        # Navigate to current position in the nested dict
        current = structure
        for p in path_stack:
            current = current[p]
        
        # Add the new entry
        current[name] = {} if is_dir else None
        
        # Update path stack if this is a directory
        if is_dir:
            path_stack.append(name)
    
    return structure[root_name] if root_name in structure else {}


def detect_format_and_parse(tree_text):
    """
    Detect the format of the tree text and parse accordingly.
    
    Args:
        tree_text (str): The text representation of the directory tree
        
    Returns:
        tuple: (dict - structure, str - format type)
    """
    # Check if it contains ASCII tree characters
    if any(char in tree_text for char in ['├', '└', '│', '─']):
        return parse_ascii_tree(tree_text), "ASCII tree"
    else:
        return parse_indented_tree(tree_text), "Indented"


def create_directory_structure(base_path, structure, update_callback=None):
    """
    Create the directory structure based on the nested dictionary.
    
    Args:
        base_path (str): The base path where the structure will be created
        structure (dict): A nested dictionary representing the directory structure
        update_callback (callable): Optional callback to update UI with progress
    """
    items_created = 0
    total_items = count_items(structure)
    
    for name, contents in structure.items():
        # Skip comments (entries starting with #)
        if name.startswith('#'):
            continue
            
        path = os.path.join(base_path, name)
        
        if contents is None:
            # This is a file
            status = f"Creating file: {path}"
            if update_callback:
                update_callback(status, items_created / total_items * 100)
            try:
                # Create parent directories if they don't exist
                os.makedirs(os.path.dirname(path), exist_ok=True)
                # Create an empty file
                open(path, 'w').close()
                items_created += 1
            except Exception as e:
                raise RuntimeError(f"Error creating file {path}: {e}")
        else:
            # This is a directory
            status = f"Creating directory: {path}"
            if update_callback:
                update_callback(status, items_created / total_items * 100)
            try:
                os.makedirs(path, exist_ok=True)
                items_created += 1
                # Recursively create the contents
                create_directory_structure(path, contents, update_callback)
            except Exception as e:
                raise RuntimeError(f"Error creating directory {path}: {e}")


def count_items(structure):
    """Count total number of items (files and directories) in the structure"""
    count = 0
    for name, contents in structure.items():
        if not name.startswith('#'):  # Skip comments
            count += 1  # Count this item
            if contents is not None:  # If it's a directory, count its contents
                count += count_items(contents)
    return count


class DirectoryTreeCreatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Directory Tree Creator")
        master.geometry("800x600")
        master.minsize(600, 400)
        
        # Create main frame
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create intro label
        intro_text = "Enter your directory tree structure below. The application supports both indented format and ASCII tree format."
        intro_label = ttk.Label(main_frame, text=intro_text, wraplength=780)
        intro_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create example frame with tabs
        example_frame = ttk.Notebook(main_frame)
        
        # Indented format example
        indented_example = ttk.Frame(example_frame)
        indented_text = """Example indented format:
project/
    src/
        main.py
        utils.py
    docs/
        index.md
    README.md"""
        indented_label = ttk.Label(indented_example, text=indented_text, justify=tk.LEFT)
        indented_label.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # ASCII tree format example
        ascii_example = ttk.Frame(example_frame)
        ascii_text = """Example ASCII tree format:
project/
├── config.py                    # Configuration settings
├── main.py                      # Entry point
├── data/
│   └── .gitkeep
└── utils/
    ├── __init__.py
    └── logger.py"""
        ascii_label = ttk.Label(ascii_example, text=ascii_text, justify=tk.LEFT)
        ascii_label.pack(fill=tk.BOTH, padx=10, pady=10)
        
        example_frame.add(indented_example, text="Indented Format")
        example_frame.add(ascii_example, text="ASCII Tree Format")
        example_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create text area for input
        self.input_frame = ttk.LabelFrame(main_frame, text="Directory Tree Input")
        self.input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree_text = scrolledtext.ScrolledText(
            self.input_frame, wrap=tk.NONE, width=40, height=10, font=("Consolas", 10)
        )
        self.tree_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frame for output path selection
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        path_label = ttk.Label(path_frame, text="Output directory:")
        path_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.output_path = tk.StringVar(value=os.path.abspath("."))
        path_entry = ttk.Entry(path_frame, textvariable=self.output_path, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(path_frame, text="Browse...", command=self.browse_output_path)
        browse_button.pack(side=tk.RIGHT)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        load_file_button = ttk.Button(button_frame, text="Load from File", command=self.load_from_file)
        load_file_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create a progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, 
                                        length=100, mode='determinate', 
                                        variable=self.progress_var)
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress.pack_forget()  # Hide initially
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                      wraplength=780, foreground="blue")
        self.status_label.pack(fill=tk.X)
        
        # Create button
        self.create_button = ttk.Button(
            button_frame, text="Create Directory Structure", 
            command=self.create_structure, style="Accent.TButton"
        )
        self.create_button.pack(side=tk.RIGHT)
        
        # Configure styles
        self.setup_styles()
        
        # Set initial status
        self.status_var.set("Ready. Enter your directory structure above.")
    
    def setup_styles(self):
        """Set up custom styles for the application"""
        style = ttk.Style()
        
        # Try to use a modern theme if available
        try:
            style.theme_use("clam")  # 'clam' is usually available across platforms
        except tk.TclError:
            pass  # Use default theme if 'clam' is not available
        
        # Create a custom style for the primary action button
        style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
    
    def browse_output_path(self):
        """Open directory browser dialog and update the output path"""
        try:
            # Start from home directory if current directory is inaccessible
            initial_dir = self.output_path.get()
            if not os.access(initial_dir, os.R_OK):
                initial_dir = os.path.expanduser("~")
                
            directory = filedialog.askdirectory(
                initialdir=initial_dir,
                title="Select Output Directory"
            )
            if directory:  # If user didn't cancel
                self.output_path.set(directory)
                
                # Check write permission immediately to provide feedback
                if not os.access(directory, os.W_OK):
                    messagebox.showwarning(
                        "Permission Warning", 
                        f"You may not have write permission to '{directory}'.\n\n"
                        "You can still try to create the structure, but it might fail."
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting directory: {e}")
    
    def load_from_file(self):
        """Load tree structure from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Tree Structure File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:  # If user didn't cancel
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.tree_text.delete(1.0, tk.END)
                self.tree_text.insert(tk.END, content)
                self.status_var.set(f"Loaded structure from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def update_progress(self, status, progress_value):
        """Update the progress bar and status label"""
        self.status_var.set(status)
        self.progress_var.set(progress_value)
        self.master.update_idletasks()  # Force update of the UI
    
    def create_structure(self):
        """Parse the tree and create the directory structure"""
        tree_text = self.tree_text.get(1.0, tk.END)
        output_path = self.output_path.get()
        
        if not tree_text.strip():
            messagebox.showerror("Error", "Please enter a directory tree structure")
            return
        
        # Check if we have write access to the parent directory
        parent_dir = os.path.dirname(output_path) or '.'
        if not os.access(parent_dir, os.W_OK):
            messagebox.showerror(
                "Permission Denied", 
                f"You don't have permission to write to '{parent_dir}'.\n\n"
                "Please select a different location or run the application with elevated privileges."
            )
            return
            
        if not os.path.exists(output_path):
            response = messagebox.askyesno(
                "Output Directory Not Found", 
                f"The directory '{output_path}' does not exist. Create it?"
            )
            if response:
                try:
                    os.makedirs(output_path, exist_ok=True)
                except PermissionError:
                    messagebox.showerror(
                        "Permission Denied", 
                        f"You don't have permission to create '{output_path}'.\n\n"
                        "Please select a different location or run the application with elevated privileges."
                    )
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory: {e}")
                    return
            else:
                return
                
        # Check if we have write access to the output directory
        elif not os.access(output_path, os.W_OK):
            messagebox.showerror(
                "Permission Denied", 
                f"You don't have permission to write to '{output_path}'.\n\n"
                "Please select a different location or run the application with elevated privileges."
            )
            return
        
        # Disable buttons during processing
        self.create_button.configure(state=tk.DISABLED)
        self.progress.pack(fill=tk.X, pady=(0, 5))  # Show progress bar
        
        try:
            # Parse the tree
            structure, format_type = detect_format_and_parse(tree_text)
            
            # Show what we detected
            self.status_var.set(f"Detected {format_type} format. Creating structure...")
            self.master.update_idletasks()  # Force update of the UI
            
            # Create the structure
            try:
                create_directory_structure(output_path, structure, self.update_progress)
            except PermissionError:
                messagebox.showerror(
                    "Permission Denied", 
                    "Permission denied while creating files or directories.\n\n"
                    "Please select a different location or run the application with elevated privileges."
                )
                return
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Directory structure created successfully in:\n{os.path.abspath(output_path)}"
            )
            self.status_var.set("Directory structure created successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {e}")
        finally:
            # Re-enable buttons and hide progress bar
            self.create_button.configure(state=tk.NORMAL)
            self.progress.pack_forget()  # Hide progress bar


def main():
    """Main function to start the application"""
    root = tk.Tk()
    
    # Set a safe default directory (user's home directory)
    default_dir = os.path.expanduser("~")
    
    # Create the application
    app = DirectoryTreeCreatorApp(root)
    app.output_path.set(default_dir)
    
    # Set app icon if available
    try:
        # On Windows
        root.iconbitmap("folder.ico")
    except:
        # Icon not found or not on Windows, use default
        pass
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()