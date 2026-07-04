#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# Filename: imgvid.py
# Project: CB9Lib - Shared Library
# Version: 1.0
# Description: Image utilities for thumbnail creation and listing
# Maintainer: Cloud Box 9 Inc.
# Last Modified Date: 2025-10-24
# -----------------------------------------------------------------------------
# Function List: 
# -----------------------------------------------------------------------------
# create_thumb_resize(src_path: str, max_width: int = 150, max_height: int = 150, suffix: str = "_tmb") -> str|bool
#     Create a resized thumbnail from source image
#     src_path: Path to source image (absolute or relative)
#              Example: "/Users/user/images/photo.jpg" or "images/photo.jpg"
#     max_width: Maximum thumbnail width in pixels
#     max_height: Maximum thumbnail height in pixels
#     suffix: Suffix to add to thumbnail filename
#     Returns: Path to created thumbnail or False on failure
#
# list_thumbnails(image_directory: str) -> list
#     List all thumbnail files in a directory
#     image_directory: Path to directory containing thumbnails (absolute or relative)
#                      Example: "/Users/user/images" or "images"
#     Returns: List of thumbnail filenames
#
# -----------------------------------------------------------------------------
# Revision History:
# -----------------------------------------------------------------------------
# v1.0 (2025-10-24)
#   • Converted from PHP imgVid.php
#   • Image thumbnail creation with aspect ratio preservation
#   • PNG and JPEG support with transparency handling
#   • List thumbnails ending in _tmb.jpg
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from typing import Union, List
from PIL import Image


def create_thumb_resize(
    src_path: str,
    max_width: int = 150,
    max_height: int = 150,
    suffix: str = "_tmb"
) -> Union[str, bool]:
    """
    Create a resized thumbnail from source image maintaining aspect ratio.

    Args:
        src_path: Path to source image file (absolute or relative)
                 Example: "/Users/user/images/photo.jpg"
        max_width: Maximum width for thumbnail
        max_height: Maximum height for thumbnail
        suffix: Suffix to add to thumbnail filename

    Returns:
        Path to created thumbnail or False on failure
    """
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        return False

    try:
        # Open image
        img = Image.open(src_path)
        width, height = img.size
        img_format = img.format

        if not img_format:
            print(f"Invalid image file: {src_path}")
            return False

        # Calculate aspect ratio
        aspect_ratio = width / height

        # Calculate new dimensions
        if width > max_width or height > max_height:
            if width / max_width > height / max_height:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
        else:
            new_width = width
            new_height = height

        # Create thumbnail
        thumb = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Build destination filename
        path_obj = Path(src_path)
        ext = path_obj.suffix.lower()

        # Determine extension based on format
        if img_format == 'JPEG':
            ext = '.jpg'
        elif img_format == 'PNG':
            ext = '.png'

        dest_path = path_obj.parent / f"{path_obj.stem}{suffix}{ext}"

        # Save thumbnail
        if img_format == 'JPEG':
            thumb.save(dest_path, 'JPEG', quality=90)
        elif img_format == 'PNG':
            thumb.save(dest_path, 'PNG', optimize=True)
        else:
            print(f"Unsupported format: {img_format}")
            return False

        print(f"Thumbnail created: {dest_path}")
        return str(dest_path)

    except Exception as e:
        print(f"Failed to create thumbnail for {src_path}: {e}")
        return False


def list_thumbnails(image_directory: str) -> List[str]:
    """
    List all thumbnail files (ending in _tmb.jpg) in a directory.

    Args:
        image_directory: Path to directory containing images (absolute or relative)
                        Example: "/Users/user/images"

    Returns:
        List of thumbnail filenames
    """
    accepted_extension = ".jpg"
    thumbnails = []

    # Ensure directory exists
    if not os.path.isdir(image_directory):
        print(f"Error: '{image_directory}' is not a valid directory.")
        return []

    try:
        # List files in directory
        for file in os.listdir(image_directory):
            full_path = os.path.join(image_directory, file)

            if os.path.isfile(full_path):
                path_obj = Path(file)
                filename_no_ext = path_obj.stem
                file_ext = path_obj.suffix.lower()

                # Check for .jpg and ending in _tmb
                if file_ext == accepted_extension and filename_no_ext.endswith("_tmb"):
                    thumbnails.append(file)

        # Print thumbnails comma-separated (matching PHP behavior)
        print(",".join(thumbnails))

    except Exception as e:
        print(f"Error listing thumbnails: {e}")

    return thumbnails
