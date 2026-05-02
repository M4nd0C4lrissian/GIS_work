from pathlib import Path

def is_empty_folder(directory_path):
    path = Path(directory_path)
    # iterdir() returns a generator; not any() checks if it's empty
    return not any(path.iterdir())

def path_exists(file_path):
    path = Path(file_path)
    
    return path.is_file()