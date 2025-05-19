import os


def get_all_images_with_folders(base_path):
    """
    Explore all the images in the directory and subdirectories.
    Return a dictionary where the keys are folder names and the values
    are paths to the first image in each folder.
    """
    folder_image_dict = {}
    if not os.path.exists(base_path):
        raise ValueError(f"Directory {base_path} does not exist.")

    for root, dirs, files in os.walk(base_path):
        # Ignore the base path itself if it doesn't have images
        if root == base_path:
            continue

        # Get folder name
        folder_name = os.path.basename(root)

        # Filter only image files (you can adjust extensions)
        image_files = [
            f
            for f in files
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]

        # Add the first image found to the dictionary
        if image_files:
            folder_image_dict[folder_name] = os.path.join(root, image_files[0])

    return folder_image_dict