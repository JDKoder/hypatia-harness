import os
LIBRARY_DIR = "library"
print(f"Current Working Directory: {os.getcwd()}")
if os.path.exists(LIBRARY_DIR):
    files = os.listdir(LIBRARY_DIR)
    print(f"Files found in '{LIBRARY_DIR}': {files}")
else:
    print(f"The directory '{LIBRARY_DIR}' does not exist!")
