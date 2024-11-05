import os
import cv2
import numpy as np
from pathlib import Path


def convert_dota_to_yolo_obb(label_path, img_path):
    """
    Convert DOTA dataset format to YOLO OBB format
    DOTA format: x1 y1 x2 y2 x3 y3 x4 y4 class difficult
    YOLO OBB format: class_index x1 y1 x2 y2 x3 y3 x4 y4 (normalized 0-1)
    """
    # Read image to get dimensions
    img = cv2.imread(img_path)
    if img is None:
        print(f"Warning: Could not read image {img_path}")
        return None

    img_height, img_width = img.shape[:2]

    def normalize_coordinates(x, y):
        """Normalize coordinates to 0-1 range"""
        return x / img_width, y / img_height

    converted_lines = []

    # try:
    with open(label_path, 'r') as f:
        # Skip the header lines
        lines = f.readlines()[2:]  # Skip imagesource and gsd lines

        for line in lines:
            parts = line.strip().split()

            # Extract coordinates and class info
            x1, y1, x2, y2, x3, y3, x4, y4 = map(float, parts[:8])
            class_name = parts[9]
            difficult = int(parts[-1])

            # Convert class name to index
            class_index = 0 if class_name == "small-vehicle" else 1  # large-vehicle

            # Calculate remaining coordinates for rectangle
            # x3, y3 = x2, y2  # bottom-right
            # x4, y4 = x1, y2  # bottom-left

            # Normalize all coordinates
            x1_norm, y1_norm = normalize_coordinates(x1, y1)
            x2_norm, y2_norm = normalize_coordinates(x2, y1)
            x3_norm, y3_norm = normalize_coordinates(x3, y3)
            x4_norm, y4_norm = normalize_coordinates(x4, y4)

            # Format in YOLO OBB style
            yolo_line = f"{class_index} {x1_norm:.6f} {y1_norm:.6f} {x2_norm:.6f} {y2_norm:.6f} "
            yolo_line += f"{x3_norm:.6f} {y3_norm:.6f} {x4_norm:.6f} {y4_norm:.6f}"

            converted_lines.append(yolo_line)

    return converted_lines
    # except Exception as e:
    #     print(f"Error processing {label_path}: {str(e)}")
    #     return None


def process_dataset(image_dir, label_dir, output_dir):
    """
    Process entire dataset converting DOTA format to YOLO OBB format
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all label files
    label_files = [f for f in os.listdir(label_dir) if f.endswith('.txt')]

    total_files = len(label_files)
    processed_files = 0
    failed_files = 0

    print(f"Found {total_files} label files to process...")

    for label_file in label_files:
        # Construct paths
        label_path = os.path.join(label_dir, label_file)
        image_file = label_file.replace('.txt', '.png')  # Adjust extension if needed
        image_path = os.path.join(image_dir, image_file)

        # Skip if image doesn't exist
        if not os.path.exists(image_path):
            print(f"Warning: Image not found for {label_file}, trying other extensions...")
            # Try other common extensions
            for ext in ['.jpg', '.jpeg', '.tiff']:
                image_path = os.path.join(image_dir, label_file.replace('.txt', ext))
                if os.path.exists(image_path):
                    break
            else:
                print(f"Error: No matching image found for {label_file}")
                failed_files += 1
                continue

        # Convert the label file
        converted_lines = convert_dota_to_yolo_obb(label_path, image_path)

        if converted_lines is not None:
            # Save converted format
            output_path = os.path.join(output_dir, label_file)
            with open(output_path, "w") as f:
                for line in converted_lines:
                    f.write(line + "\n")
            processed_files += 1
        else:
            failed_files += 1

        # Print progress
        if processed_files % 100 == 0:
            print(f"Processed {processed_files}/{total_files} files...")

    print(f"\nConversion completed!")
    print(f"Successfully processed: {processed_files} files")
    print(f"Failed: {failed_files} files")
    print(f"Total: {total_files} files")
    print(f"Converted labels saved to: {output_dir}")


if __name__ == "__main__":
    # Directory paths
    image_dir = "images"  # Directory containing images
    label_dir = "labels/DOTA-v1.5_val"  # Directory containing DOTA format labels
    output_dir = f"{label_dir}_RESULT"  # Directory for output YOLO OBB format labels

    # Process the entire dataset
    process_dataset(image_dir, label_dir, output_dir)
