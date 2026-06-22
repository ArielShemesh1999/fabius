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
"""Generates sample product data and images for the product catalog."""

import asyncio
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import types
from pydantic import BaseModel, Field

# --- Configuration and Initialization ---
load_dotenv()

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GCP_LOCATION", "us-east1")
COMPANY_NAME = os.getenv("COMPANY_NAME", "ACME Corp")

# Output directories
OUTPUT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "static", "uploads", "products"
    )
)
BRANDING_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "static", "uploads", "branding"
    )
)

# --- User Configuration ---
# Modify these constants to change the generation parameters
PRODUCT_DESCRIPTION = (
    "A department store offering a wide range of products including "
    "running shoes, dutch oven, smart bulb, headphones, and a Christmas tree."
)
PRODUCT_COUNT = 5
# Set LOGO_DESCRIPTION to None to skip logo generation
LOGO_DESCRIPTION = (
    f"A simple, modern logo with stylized letter for {COMPANY_NAME}"
)

# --- Gemini API Client ---
# Client is initialized in main()

# --- Pydantic Models ---


class ProductImagePlan(BaseModel):
    """Plan for a single product image."""

    filename: str = Field(
        ..., description="The filename for the image (e.g. acme_widget_v1.png)"
    )
    image_prompt: str = Field(..., description="Prompt to generate the image")


class ProductPlanResponse(BaseModel):
    """The overall response schema for the product plan generation."""

    products: list[ProductImagePlan]


# --- Core Functions ---


async def generate_plan(
    client: genai.Client, company_name: str, description: str, count: int
) -> list[ProductImagePlan] | None:
    """Generates a plan for creating product images."""
    prompt = f"""
    You are an expert creative director. Create a plan to generate {count}
    high-quality product images for a company named "{company_name}".

    The product description is: "{description}".

    For each product, provide:
    1. A unique, descriptive filename (ending in .png).
    2. A detailed, high-quality image generation prompt. The prompt should
       describe a professional product shot, photorealistic, 8k resolution.
       The prompt MUST emphasize that the product is isolated on a clean,
       solid white background, with studio lighting, and no other objects or
       props in the frame.
       Focus on the visual details of the product based on the description.
       The full view of the product should be the main focus of the image.

       CRITICAL: The prompt MUST include instructions on how to naturally
       incorporate the company logo into the product or its packaging.
       The logo integration should be subtle, realistic, and match the
       product's style and material.
       Examples:
       - A branded tag on clothing.
       - An embossed logo on a leather good.
       - A printed logo on a ceramic mug.
       - A branded ornament on a Christmas tree.
       - A sticker or label on a tech gadget.
       The goal is for the branding to look like a natural part of the
       physical product.

    Output a JSON object with a 'products' key containing a list of these plans
    """

    try:
        logging.info("🤖 Generating product plan with Gemini...")
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProductPlanResponse,
            ),
        )
        parsed_response = ProductPlanResponse.model_validate_json(response.text)
        return parsed_response.products
    except (google_exceptions.InternalServerError, ValueError) as e:
        logging.error("Error generating plan: %s", e)
        return None


async def generate_logo_prompt(
    client: genai.Client, company_name: str, logo_description: str
) -> str | None:
    """Generates a prompt for the logo."""
    prompt = f"""
    You are an expert creative director. Write a detailed image generation
    prompt for a logo for "{company_name}".

    Logo Description: "{logo_description}"
    The prompt should describe a high-quality, professional logo design,
    suitable for a business.
    It should be a vector-style graphic or a clean, high-resolution image on a
    solid background (preferably white or transparent if possible, but solid
    white is fine).
    Output only the prompt text.
    """
    try:
        logging.info("🤖 Generating logo prompt with Gemini...")
        response = await client.aio.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="text/plain",
            ),
        )
        return response.text.strip()
    except (google_exceptions.InternalServerError, ValueError) as e:
        logging.error("Error generating logo prompt: %s", e)
        return None


async def generate_and_save_image(
    client: genai.Client,
    prompt: str,
    output_path: str,
    input_parts: list[types.Part] | None = None,
) -> bytes | None:
    """
    Generates an image and saves it to the specified path.
    Returns image bytes on success.
    """
    try:
        logging.info(
            "🎨 Generating image for: %s...", os.path.basename(output_path)
        )

        contents = [prompt]
        if input_parts:
            contents.extend(input_parts)

        response = await client.aio.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="9:16",
                ),
            ),
        )

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    logging.info("✅ Saved: %s", output_path)
                    return image_bytes
        logging.warning(
            "❌ Failed to generate image for %s", os.path.basename(output_path)
        )
        return None

    except (google_exceptions.InternalServerError, ValueError) as e:
        logging.error(
            "Error generating image %s: %s", os.path.basename(output_path), e
        )
        return None


def _initialize_directories():
    """Ensures output directories exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(BRANDING_DIR, exist_ok=True)


def _print_configuration():
    """Prints the current configuration."""
    logging.info("--- Configuration ---")
    logging.info("Company: %s", COMPANY_NAME)
    logging.info("Description: %s", PRODUCT_DESCRIPTION)
    logging.info("Count: %s", PRODUCT_COUNT)
    logging.info("Logo Description: %s", LOGO_DESCRIPTION)


async def _generate_initial_plans(client: genai.Client):
    """Generates the product plan and logo prompt in parallel."""
    logging.info("🤖 Sending requests to Gemini...")
    tasks = [
        generate_plan(client, COMPANY_NAME, PRODUCT_DESCRIPTION, PRODUCT_COUNT)
    ]
    if LOGO_DESCRIPTION:
        tasks.append(
            generate_logo_prompt(client, COMPANY_NAME, LOGO_DESCRIPTION)
        )

    results = await asyncio.gather(*tasks)
    plan = results[0]
    logo_prompt = results[1] if len(results) > 1 else None
    return plan, logo_prompt


def _print_generated_plan(
    plan: list[ProductImagePlan], logo_prompt: str | None
):
    """Prints the generated plan and logo prompt."""
    logging.info("\n--- Generated Plan ---")
    for i, item in enumerate(plan):
        logging.info("%s. %s", i + 1, item.filename)
        logging.info("   Prompt: %s...", item.image_prompt[:100])

    if logo_prompt:
        logging.info("\n[Logo] logo.png")
        logging.info("   Prompt: %s...", logo_prompt[:100])


def _confirm_generation(
    plan: list[ProductImagePlan], logo_prompt: str | None
) -> bool:
    """Asks the user to confirm image generation."""
    while True:
        confirm = (
            input(
                "\nProceed with image generation? (y/n) or 'x' to expand prompts: "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            return True
        if confirm == "n":
            logging.info("Aborted.")
            return False
        if confirm == "x":
            logging.info("\n--- Expanded Prompts ---")
            for i, item in enumerate(plan):
                logging.info("\n%s. %s", i + 1, item.filename)
                logging.info("   Prompt: %s", item.image_prompt)
            if logo_prompt:
                logging.info("\n[Logo] logo.png")
                logging.info("   Prompt: %s", logo_prompt)
            logging.info("\n------------------------")
        else:
            logging.warning("Invalid input. Please enter 'y', 'n', or 'x'.")


async def _generate_logo(
    client: genai.Client, logo_prompt: str
) -> types.Part | None:
    """Generates the logo image."""
    logo_path = os.path.join(BRANDING_DIR, "logo.png")
    logo_bytes = await generate_and_save_image(client, logo_prompt, logo_path)
    if logo_bytes:
        return types.Part.from_bytes(data=logo_bytes, mime_type="image/png")
    return None


async def _generate_product_images(
    client: genai.Client,
    plan: list[ProductImagePlan],
    logo_part: types.Part | None,
):
    """Generates product images in parallel."""
    image_tasks = []
    for item in plan:
        file_path = os.path.join(OUTPUT_DIR, item.filename)
        input_parts = [logo_part] if logo_part else None
        image_tasks.append(
            generate_and_save_image(
                client, item.image_prompt, file_path, input_parts=input_parts
            )
        )

    if image_tasks:
        await asyncio.gather(*image_tasks)


async def main():
    """Main execution flow."""
    _initialize_directories()
    _print_configuration()

    try:
        with genai.Client(
            vertexai=True, project=PROJECT, location=LOCATION
        ) as client:
            plan, logo_prompt = await _generate_initial_plans(client)

            if not plan:
                logging.error("❌ Failed to generate plan.")
                return

            _print_generated_plan(plan, logo_prompt)

            if not _confirm_generation(plan, logo_prompt):
                return

            logging.info("\n🚀 Starting image generation...")

            logo_part = None
            if logo_prompt:
                logo_part = await _generate_logo(client, logo_prompt)

            await _generate_product_images(client, plan, logo_part)

            logging.info("\n✨ All done!")

    except google_exceptions.GoogleAPICallError as e:
        logging.error("Failed to generate content: %s", e, exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Suppress some logging from libraries to keep output clean for the user
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\nCancelled by user.")
