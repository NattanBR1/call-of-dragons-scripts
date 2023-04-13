import pytesseract
import os
from PIL import Image, ImageFilter
import cv2
import numpy as np
import os
import datetime
from collections import defaultdict
import csv


def get_files_in_directory(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

def preprocess_image(file_path):
    # Load the image
    image = Image.open(file_path)

    # Convert the image to grayscale
    image = image.convert("L")

    # Apply Gaussian blur to reduce noise
    image = image.filter(ImageFilter.GaussianBlur(radius=1.2))

    # Convert the PIL Image to a numpy array for further processing with OpenCV
    image = np.array(image)

    # Apply Otsu's thresholding for better binarization
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Apply dilation to connect broken characters
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)

    # Resize the image to improve text recognition
    image = cv2.resize(image, (image.shape[1] * 2, image.shape[0] * 2), interpolation=cv2.INTER_CUBIC)

    # Convert the numpy array back to a PIL Image
    image = Image.fromarray(image)

    return image

def process_screenshot(file_path):
    # Preprocess the image
    image = preprocess_image(file_path)

    # Extract text from the preprocessed screenshot
    extracted_text = pytesseract.image_to_string(image)

    # Split the OCR output into lines
    lines = extracted_text.splitlines()

    # Initialize an empty list to store the extracted user data
    user_data = []

    # Remove 'Power' lines from the OCR output
    lines = [line for line in lines if line.strip() != 'Power']
    print(lines)

    # Iterate through the lines and extract usernames and power levels
    i = 0
    while i < len(lines) - 1:
        username = lines[i].strip()
        if len(username) > 2:
            power_line = lines[i + 1].strip().replace(',', '')
            if power_line.isdigit():
                power = power_line
                user_data.append((username, power))
                i += 1
        i += 1
    print(user_data)
    return user_data

def process_screenshots(file_paths):
    all_user_data = defaultdict(list)
    for file_path in file_paths:
        # Get the current date
        date = datetime.datetime.now().date()

        # Process the screenshot and store the user data in the dictionary
        user_data = process_screenshot(file_path)
        all_user_data[date].extend(user_data)

    return all_user_data

def update_spreadsheet(all_user_data):
    with open("user_data.csv", mode="w", newline="") as csvfile:
        fieldnames = ["date", "username", "power"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for date, user_data in all_user_data.items():
            for username, power in user_data:
                writer.writerow({"date": date, "username": username, "power": power})


# Set the directory containing the screenshots
screenshot_directory = "screenshots"

# Get the list of file paths in the directory
file_paths = get_files_in_directory(screenshot_directory)

# Process the screenshots and group the data by date
all_user_data = process_screenshots(file_paths)

# Update the CSV file with the extracted data
update_spreadsheet(all_user_data)
