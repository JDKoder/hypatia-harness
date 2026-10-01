import os.path

def get_files_info(working_directory, directory=None):
    cwd_abs_path = os.path.abspath(working_directory)
    dir_abs_path = cwd_abs_path
    if directory:
        dir_abs_path = os.path.abspath(os.path.join(cwd_abs_path, directory))
    if not dir_abs_path.startswith(cwd_abs_path):
        return f'Error: Cannot list "{directory}" as it is outside of the permitted working directory'

    is_dir = os.path.isdir(dir_abs_path)
    if not is_dir:
        return f'Error: "{directory}" is not a directory'

    # print(f"is_dir={is_dir}")
    if is_dir:
        dir_listing = []
        for f in os.listdir(dir_abs_path):
            filepath = os.path.join(dir_abs_path, f)
            filesize = os.path.getsize(filepath)
            file_is_dir = os.path.isdir(filepath)
            dir_listing.append(f"- {f}: file_size={filesize} bytes, is_dir={file_is_dir} ")
            # print(f"- {f}: file_size={filesize} bytes, is_dir={file_is_dir} ")
        return "\n".join(dir_listing)


def get_file_content(working_directory, file_path):
    cwd_abs_path = os.path.abspath(working_directory)
    file_abs_path = cwd_abs_path
    if file_path:
        file_abs_path = os.path.abspath(os.path.join(cwd_abs_path, file_path))
    if not file_abs_path.startswith(cwd_abs_path):
        return f'Error: Cannot read "{file_path}" as it is outside of the permitted working directory'

    is_file = os.path.isfile(file_abs_path)
    if not is_file:
        return f'Error: File not found or is not a regular file:  "{file_path}"'

    MAX_CHARS = 10000
    file_content_string = ""
    try:
        with open(file_abs_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
    except Exception as e:
        return f'Error: failed to read file. Exception: {e}'
    return file_content_string


def write_file(working_directory, file_path, content):
    cwd_abs_path = os.path.abspath(working_directory)
    target_file = cwd_abs_path
    if file_path:
        target_file = os.path.abspath(os.path.join(cwd_abs_path, file_path))
    if not target_file.startswith(cwd_abs_path):
        return f'Error: cannot write to "{file_path}" as it is outside the permitted working directory'
    path_list = target_file.split("/")
    print(f"path_list: {path_list}")
    filename = path_list.pop()
    target_dir_path = "/".join(path_list)
    if not os.path.exists(target_dir_path):
        try:
            print(f"target_dir_path: [{target_dir_path}]")
            os.makedirs(target_dir_path)
        except FileExistsError as fe:
            return f'Error: FileExistsException, file creation failed. {fe}'
    try:
        with open(target_file, "w") as f:
            f.write(content)
    except Exception as fee:
        return f'Error: failed to open and write file {target_file}. Exception: {fee}'
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
