# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Adds whitespace padding to images to make them a 9:16 aspect ratio."""

import logging
import os

from PIL import Image


def add_padding_to_image(input_path, output_path):
    """
    Adds whitespace padding to an image to make it a 9:16 aspect ratio.
    """
    try:
        img = Image.open(input_path)
        width, height = img.size

        aspect_ratio_error = 1e-6
        target_aspect_ratio = 9.0 / 16.0
        current_aspect_ratio = float(width) / float(height)

        if abs(current_aspect_ratio - target_aspect_ratio) < aspect_ratio_error:
            img.save(output_path)
            return

        if current_aspect_ratio > target_aspect_ratio:
            new_height = int(width / target_aspect_ratio)
            new_width = width
        else:
            new_width = int(height * target_aspect_ratio)
            new_height = height

        new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))

        paste_x = (new_width - width) // 2
        paste_y = (new_height - height) // 2

        new_img.paste(img, (paste_x, paste_y))
        new_img.save(output_path)

    except (OSError, FileNotFoundError) as e:
        logging.error("Error processing %s: %s", input_path, e)


def process_images_in_folder(input_folder, output_folder):
    """
    Processes all images in the input folder and saves to the output folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            add_padding_to_image(input_path, output_path)
            logging.info("Processed %s", filename)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    INPUT_DIR = "static/uploads/products"
    OUTPUT_DIR = "static/generated/padded_products"
    process_images_in_folder(INPUT_DIR, OUTPUT_DIR)
