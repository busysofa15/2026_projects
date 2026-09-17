import os
import sys
import shutil
extension_blueprint = {
    ".mp3": "audios",
    ".wav": "audios",
    ".mp4": "videos",
    ".mov": "videos",
    ".mkv": "videos",
    ".png": "images",
    ".jpeg": "images",
    ".jpg": "images",
    ".webp": "images",
    ".heic": "images"
}
while True:
    source_directory = input(
        "Enter the path of the messy folder😁: ").strip('"')
    if not os.path.isabs(source_directory):
        print("Invalid path re enter your desired path")
        Proceed_or_cancel = input(
            "type Y to try again or any other key to cancel: ")
        if Proceed_or_cancel == ("y"):
            continue
        if not Proceed_or_cancel == ("y"):
            break
    if os.path.isdir(source_directory):
        target_directory = os.path.join(source_directory, "organized files")
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        unsorted_files = os.listdir(source_directory)
        for file in unsorted_files:
            if os.path.isdir(os.path.join(source_directory, file)):
                continue
            name, extensions = os.path.splitext(file)
            folder_name = extension_blueprint.get(extensions.lower(), "others")
            folder = os.path.join(target_directory, folder_name)
            if not os.path.exists(folder):
                os.makedirs(folder)
            shutil.move(os.path.join(source_directory, file),
                        os.path.join(folder, file))
        print("ha your files have been organised succesfully 👌👍")
    want_to_continue_or_exit = input(
        "type Y to continue any other letter to exit: ")
    if want_to_continue_or_exit == str("y"):
        continue
    if not want_to_continue_or_exit == str("y"):
        break
