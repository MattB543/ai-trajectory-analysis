"""
Script created to process non-square images in the images folder.
Created at the direct request of the user to:
1. Identify non-square images
2. Backup non-square images to old_images folder
3. Crop images in place to be square using center-cropping

User requested: Check all images, backup non-square ones, and center-crop them to square dimensions.
"""

import os
from pathlib import Path
from PIL import Image
import shutil
from datetime import datetime

def log_ok(message):
    """Log success message with [OK] tag"""
    print(f"[OK] {message}")

def log_error(message):
    """Log error message with [ERROR] tag"""
    print(f"[ERROR] {message}")

def log_info(message):
    """Log informational message with [INFO] tag"""
    print(f"[INFO] {message}")

def get_image_dimensions(image_path):
    """Get the dimensions of an image"""
    try:
        with Image.open(image_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        log_error(f"Could not read image {image_path}: {e}")
        return None

def is_square(width, height):
    """Check if image is square"""
    return width == height

def center_crop_to_square(image_path, output_path):
    """
    Crop image to square by taking the center portion.
    Uses the smaller dimension as the target size.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size

            # Calculate the size of the square (smaller dimension)
            min_dimension = min(width, height)

            # Calculate the cropping box (left, upper, right, lower)
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension

            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))

            # Save the cropped image
            cropped_img.save(output_path, quality=95, optimize=True)

            return True
    except Exception as e:
        log_error(f"Failed to crop {image_path}: {e}")
        return False

def main():
    # Define paths
    project_root = Path(r"C:\Users\matth\projects\ai-trajectory-analysis")
    images_folder = project_root / "images"
    old_images_folder = project_root / "old_images"

    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    log_info("Starting image processing script...")
    log_info(f"Images folder: {images_folder}")

    # Check if images folder exists
    if not images_folder.exists():
        log_error(f"Images folder does not exist: {images_folder}")
        return

    # Create old_images folder if it doesn't exist
    if not old_images_folder.exists():
        old_images_folder.mkdir(parents=True)
        log_ok(f"Created backup folder: {old_images_folder}")
    else:
        log_info(f"Backup folder already exists: {old_images_folder}")

    # Get all image files
    image_files = []
    for ext in image_extensions:
        image_files.extend(images_folder.glob(f"*{ext}"))

    if not image_files:
        log_info("No image files found in the images folder.")
        return

    log_info(f"Found {len(image_files)} image files to process")

    # Process images
    non_square_images = []
    square_images = []
    processed_count = 0
    failed_count = 0

    for image_path in image_files:
        log_info(f"Checking: {image_path.name}")

        dimensions = get_image_dimensions(image_path)
        if dimensions is None:
            failed_count += 1
            continue

        width, height = dimensions

        if is_square(width, height):
            log_info(f"  Already square ({width}x{height})")
            square_images.append({
                'name': image_path.name,
                'dimensions': f"{width}x{height}"
            })
        else:
            log_info(f"  Non-square detected ({width}x{height})")
            non_square_images.append({
                'name': image_path.name,
                'original_dimensions': f"{width}x{height}",
                'target_dimension': min(width, height)
            })

            # Backup the original image
            backup_path = old_images_folder / image_path.name
            try:
                shutil.copy2(image_path, backup_path)
                log_ok(f"  Backed up to: {backup_path.name}")
            except Exception as e:
                log_error(f"  Failed to backup {image_path.name}: {e}")
                failed_count += 1
                continue

            # Crop the image in place
            if center_crop_to_square(image_path, image_path):
                new_dimensions = get_image_dimensions(image_path)
                if new_dimensions:
                    new_width, new_height = new_dimensions
                    log_ok(f"  Cropped to: {new_width}x{new_height}")
                    processed_count += 1
            else:
                failed_count += 1

    # Print summary
    print("\n" + "="*60)
    log_info("PROCESSING SUMMARY")
    print("="*60)

    log_info(f"Total images found: {len(image_files)}")
    log_info(f"Already square: {len(square_images)}")
    log_info(f"Non-square images processed: {processed_count}")

    if failed_count > 0:
        log_error(f"Failed to process: {failed_count}")

    if non_square_images:
        print("\n" + "-"*60)
        log_info("NON-SQUARE IMAGES THAT WERE CROPPED:")
        print("-"*60)
        for img_info in non_square_images:
            print(f"  - {img_info['name']}")
            print(f"    Original: {img_info['original_dimensions']}")
            print(f"    Cropped to: {img_info['target_dimension']}x{img_info['target_dimension']}")

    if square_images:
        print("\n" + "-"*60)
        log_info("IMAGES THAT WERE ALREADY SQUARE:")
        print("-"*60)
        for img_info in square_images:
            print(f"  - {img_info['name']} ({img_info['dimensions']})")

    print("\n" + "="*60)
    if processed_count > 0:
        log_ok(f"All non-square images have been backed up to: {old_images_folder}")
        log_ok(f"Successfully cropped {processed_count} images to square dimensions")
    else:
        log_info("No images needed to be cropped")
    print("="*60)

if __name__ == "__main__":
    main()
