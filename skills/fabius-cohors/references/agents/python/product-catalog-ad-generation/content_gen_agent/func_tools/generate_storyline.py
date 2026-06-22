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

"""
Handles the generation of storylines, visual style guides,
 and asset sheets.
"""

import asyncio
import json
import logging
import time
from typing import Union

from dotenv import load_dotenv
from google import genai
from google.adk.tools import ToolContext
from google.genai import types

from content_gen_agent.func_tools.select_product import select_product_from_bq
from content_gen_agent.utils.evaluate_media import calculate_evaluation_score
from content_gen_agent.utils.gemini_utils import (
    call_gemini_image_api,
    initialize_gemini_client,
)
from content_gen_agent.utils.images import ensure_image_artifact
from content_gen_agent.utils.storytelling import STORYTELLING_INSTRUCTIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

# Initialize Gemini client
client = initialize_gemini_client()

# --- Configuration ---
STORYLINE_MODEL = "gemini-2.5-flash"
IMAGE_GEN_MODEL = "gemini-3.1-flash-image-preview"
MAX_RETRIES = 3


# pylint: disable=too-many-arguments
async def generate_storyline(
    product: str,
    target_demographic: str,
    tool_context: ToolContext,
    company_name: str,
    num_images: int = 5,
    photo_filenames: list[str] | None = None,
    style_preference: str = "photorealistic",
    user_provided_asset_sheet_filename: str | None = None,
) -> dict[str, str | None | list[dict[str, str]]]:
    """Generates a storyline, visual style guide, and asset sheet.

    Args:
        product (str): The company's product to be featured. This is used to
          search a product database if the user doesn't provide a product
          photo to you directly. Just include a short and simple search term,
          e.g. "headphones" or "shoes".
          If no matching product is found in the database, you can ask the user
          to provide an image of the product through the UI.  Then recall
          generate_storyline with the filename of the product image artifact
          in the photo_filenames input parameter.
        target_demographic (str): The target audience for the commercial.
        tool_context (ToolContext): The context for saving artifacts.
        company_name (str): The name of the company to be featured.
        num_images (int): The number of images to generate. Defaults to 5.
        photo_filenames (Optional[List[str]]): The filenames of the photo
          artifacts to include in the newly generated asset sheet. Defaults to
          None. Should include a product image if provided by the user.
          photo_filenames is ignored if user_provided_asset_sheet_filename is
          given. filenames are assumed to be Google Cloud Storage URIs if
          beginning with "gs://".
        style_preference (str): The desired visual style of the ad.
          Defaults to "photorealistic".
        user_provided_asset_sheet_filename (Optional[str]): The filename of the
          user-provided asset sheet. Defaults to None. If provided,
          photo_filenames is ignored. filename is assumed to be a Google Cloud
          Storage URI if beginning with "gs://".

    Returns:
        A dictionary containing the generated content and status.
    """
    if not client:
        logging.error("Gemini client not initialized. Check credentials.")
        return {"status": "failed", "detail": "Gemini client not initialized."}

    style_guide = (
        f"The style must be cohesive, professional, high-quality, with "
        f"minimal whitespace and a '{style_preference}' effect."
    )

    try:
        (
            image_parts,
            final_photo_filenames,
        ) = await _process_asset_sheet_input_images(
            tool_context,
            product,
            photo_filenames,
            user_provided_asset_sheet_filename,
        )
    except ValueError as e:
        return {"status": "failed", "detail": str(e)}

    story_data = _generate_storyline_text(
        product,
        target_demographic,
        num_images,
        style_guide,
        company_name,
        image_parts,
    )
    if "error" in story_data:
        return {"status": "failed", "detail": story_data["error"]}

    asset_sheet_filename = (
        user_provided_asset_sheet_filename  # will be overwritten if None
    )

    # Generate the asset sheet from scratch using the generated storyline text
    if not user_provided_asset_sheet_filename:
        if not final_photo_filenames:
            return {
                "status": "failed",
                "detail": "Failed to populate product photos.",
            }

        asset_sheet_filename = await _generate_asset_sheet_image(
            story_data, final_photo_filenames, tool_context, style_guide
        )
        if not asset_sheet_filename:
            return {
                "status": "failed",
                "detail": "Failed to generate asset sheet image.",
            }

    vsg_filename = await _save_json_artifact(
        tool_context,
        "visual_style_guide",
        story_data["visual_style_guide"],
    )
    storyline_filename = await _save_json_artifact(
        tool_context, "storyline", {"storyline": story_data.get("storyline")}
    )

    return {
        "storyline": story_data.get("storyline"),
        "asset_sheet_filename": asset_sheet_filename,
        "visual_style_guide_filename": vsg_filename,
        "storyline_filename": storyline_filename,
        "status": "success",
    }


async def _process_asset_sheet_input_images(
    tool_context: ToolContext,
    product: str,
    photo_filenames: list[str] | None = None,
    user_provided_asset_sheet_filename: str | None = None,
) -> tuple[list[types.Part], list[str]]:
    """
    tool_context (ToolContext): The context for saving artifacts.
    product (str): The company's product to be featured. This is used to search
      a product database if needed. Just include the product name.
    photo_filenames (Optional[List[str]]): The filenames of the photo
      artifacts to include in the newly generated asset sheet. Defaults to None
      photo_filenames is ignored if user_provided_asset_sheet_filename is
      given. filenames are assumed to be Google Cloud Storage URIs if beginning
      with "gs://".
    user_provided_asset_sheet_filename (Optional[str]): The filename of the
      user-provided asset sheet. Defaults to None. If provided,
      photo_filenames is ignored. filename is assumed to be a Google Cloud
      Storage URI if beginning with "gs://".
    """
    image_parts: list[types.Part] = []
    final_photo_filenames: list[str] = []

    # If we're using a user-provided asset sheet
    if user_provided_asset_sheet_filename:
        asset_sheet_filename = await ensure_image_artifact(
            user_provided_asset_sheet_filename, tool_context
        )
        if asset_sheet_filename:
            image_part = await tool_context.load_artifact(asset_sheet_filename)
            if image_part:
                image_parts.append(image_part)
            logging.info(
                "Loaded user-provided asset sheet: %s", asset_sheet_filename
            )
        else:
            raise ValueError(
                "Failed: Could not load user-provided asset sheet:"
                f" {user_provided_asset_sheet_filename}"
            )
    # If not using a user-provided asset sheet, check for individual photos
    elif photo_filenames:
        for p_filename in photo_filenames:
            ensured = await ensure_image_artifact(p_filename, tool_context)
            if ensured:
                final_photo_filenames.append(ensured)
                image_part = await tool_context.load_artifact(ensured)
                if image_part:
                    image_parts.append(image_part)

    # If no images provided at all, fall back to BQ
    if not image_parts:
        bq_filename = await _save_product_photo_artifact(product, tool_context)
        if bq_filename:
            final_photo_filenames.append(bq_filename)
            image_part = await tool_context.load_artifact(bq_filename)
            if image_part:
                image_parts.append(image_part)

    return image_parts, final_photo_filenames


# pylint: disable=too-many-arguments
def _generate_storyline_text(
    product: str,
    target_demographic: str,
    num_images: int,
    style_guide: str,
    company_name: str,
    image_parts: list[genai.types.Part] | None = None,
) -> dict[str, str | dict[str, list[dict[str, str] | str]]]:
    """Generates the storyline and visual style guide text.

    Args:
        product (str): The product to be featured.
        target_demographic (str): The target audience.
        num_images (int): The number of images to generate.
        style_guide (str): The visual style description.
        company_name (str): The name of the company to be featured.
        image_parts (Optional[List[genai.types.Part]]): Optional user-provided
          images (e.g., asset sheet, character photos). Defaults to None.

    Returns:
        A dictionary containing the storyline and visual style guide.
    """
    if not client:
        logging.error("Gemini client not initialized.")
        return {"error": "Gemini client not initialized."}

    generation_prompt = f"""
    You are a creative assistant for {company_name}. Your task is to generate
    a compelling storyline and a detailed visual style guide for a short
    commercial about the '{product}' for the '{target_demographic}'
    demographic.

    The storyline should have a before, purchasing, and after narrative. If
    generating more than 3 scenes, make the first scene a slow flyover aerial
    shot of the location without any characters.

        CRITICAL: Each generated scene must take place in a SINGLE, continuous
    setting. Do not describe multiple locations, time jumps, or cuts within a
    single scene description. Cuts can only happen between the distinct scenes
    you are generating.

    Make sure the storyline matches the following style guide: '{style_guide}'

    Your final scene should always be a shot with a logo in front and a
    beautiful, moving background. Keep the {company_name} logo prominent in
    the center frame and animate the background to make it feel dynamic.

    The visual style guide must describe the necessary imagery. Provide
    detailed descriptions of characters (with gender and age, adults only),
    each scene's locations, and a short list of critical props and assets
    (excluding the {product}).

    {STORYTELLING_INSTRUCTIONS}

    Please return the output as a single JSON object with two keys:
    "storyline" and "visual_style_guide".
    The "storyline" key must contain a single string narrative with
    {num_images} scenes.
     - Do not refer to other scenes in a scene description; be explicit about
       what each scene is about.
     - For each Scene, structure it as follows:
         # Scene _: `Title`
         ## `Description`
    The "visual_style_guide" should contain "characters", "locations", and
    "asset_sheet".
    """
    try:
        logging.info("Generating storyline and visual style guide...")
        contents = []
        if image_parts:
            contents.extend(image_parts)
            generation_prompt += """
    IMPORTANT: Write the storyline based on the attached image(s). If the
    images contain people, they are the characters that should appear in the
    story. Base your character descriptions in the visual style guide on these
    people. If the images contain products or locations, incorporate them into
    the storyline and visual style guide.
            """
        contents.append(generation_prompt)
        response = client.models.generate_content(
            model=STORYLINE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        if response.text:
            story_data = json.loads(response.text)
            logging.info(
                "Successfully generated storyline and visual style guide."
            )
            return story_data
        return {"error": "Received an empty response from the model."}
    except (json.JSONDecodeError, ValueError) as e:
        logging.error("Error generating storyline text: %s", e, exc_info=True)
        return {"error": f"Error generating storyline text: {e}"}


async def _save_product_photo_artifact(
    product: str, tool_context: ToolContext
) -> str | None:
    """
    Fetches the product's image URI from BigQuery, downloads it
    from GCS, and saves it as an artifact.

    Args:
        product (str): The product name to look up if no filename is provided.
        tool_context (ToolContext): The context for accessing and saving
          artifacts.

    Returns:
        The filename of the product photo artifact, or None on failure.
    """
    product_details = select_product_from_bq(product)
    if not product_details or "image_gcs_uri" not in product_details:
        logging.error("Product '%s' not found in BigQuery.", product)
        return None

    gcs_uri = product_details["image_gcs_uri"]

    artifact_filename = await ensure_image_artifact(gcs_uri, tool_context)
    return artifact_filename


def _process_visual_style_guide(
    visual_style_guide: dict[str, list[dict[str, str] | str]],
) -> dict[str, str]:
    """Processes the visual style guide into formatted strings.

    Args:
        visual_style_guide (Dict[str, List[Union[Dict[str, str], str]]]): The
          visual style guide dictionary.

    Returns:
        A dictionary of processed descriptions.
    """

    def format_list(items: list[dict[str, str] | str]) -> str:
        processed = []
        for item in items:
            if isinstance(item, dict):
                processed.append(" ".join(str(v) for v in item.values()))
            else:
                processed.append(str(item))
        return ", ".join(processed)

    asset_sheet_items = visual_style_guide.get("asset_sheet", [])
    characters = visual_style_guide.get("characters", [])
    locations = visual_style_guide.get("locations", [])

    return {
        "asset_sheet": format_list(asset_sheet_items),
        "characters": ". ".join(
            (
                f"{item.get('name', '')}: {item.get('description', '')}"
                if isinstance(item, dict)
                else str(item)
            )
            for item in characters
        ),
        "locations": format_list(locations),
    }


def _create_asset_sheet_prompt(
    story_data: dict[str, str | dict[str, list[dict[str, str] | str]]],
    style_guide: str,
) -> str:
    """Creates the prompt for the asset sheet image."""
    visual_style_guide = story_data.get("visual_style_guide", {})
    processed_vsg = _process_visual_style_guide(visual_style_guide)

    return f"""A visual asset sheet for a commercial.
    Instructions:
    Create a clean, organized collage displaying each of the following:
    1) Front and side profiles of each character
    2) Locations/settings for each scene
    3) The attached image(s).
    {style_guide}

    Characters: {processed_vsg["characters"]}
    Locations: {processed_vsg["locations"]}
    Assets: Attached image(s).
    """


async def _generate_and_select_best_image(
    contents: list[Union[str, "types.Part"]],
    image_prompt: str,
) -> dict[str, str | bytes]:
    """
    Generates multiple images and selects the best one based on evaluation.
    """
    tasks = [
        call_gemini_image_api(
            client=client,
            model=IMAGE_GEN_MODEL,
            contents=contents,
            image_prompt=image_prompt,
        )
        for _ in range(MAX_RETRIES)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    generation_attempts = [
        res for res in results if isinstance(res, dict) and res
    ]
    if not generation_attempts:
        logging.error("Failed to generate any asset sheet images.")
        return None

    best_attempt = max(
        generation_attempts,
        key=lambda x: calculate_evaluation_score(x.get("evaluation")),
    )

    if best_attempt["evaluation"].decision != "Pass":
        score = calculate_evaluation_score(best_attempt["evaluation"])
        logging.warning(
            "No image passed evaluation.Selecting best attempt with score: %s",
            score,
        )

    return best_attempt


async def _generate_asset_sheet_image(
    story_data: dict[str, str | dict[str, list[dict[str, str] | str]]],
    photo_filenames: list[str],
    tool_context: ToolContext,
    style_guide: str,
) -> str | dict[str, str]:
    """Generates and evaluates asset sheet images, saving the best one.

    Args:
        story_data (Dict[
            str, Union[str, Dict[str, list[Union[Dict[str, str], str]]]]
        ]): The storyline and visual style guide data.
        photo_filenames (List[str]): The filenames of the photos to include.
        tool_context (ToolContext): The context for saving artifacts.
        style_guide (str): The visual style description.

    Returns:
        The filename of the generated asset sheet, or a dict on failure.
    """
    image_prompt = _create_asset_sheet_prompt(story_data, style_guide)
    logging.info("Generating asset sheet image for prompt: '%s'", image_prompt)

    contents = [image_prompt]
    for filename in photo_filenames:
        try:
            photo_part = await tool_context.load_artifact(filename)
            if photo_part:
                contents.append(photo_part)
        except (FileNotFoundError, ValueError) as e:
            logging.error(
                "Failed to load one of the photo artifacts '%s': %s",
                filename,
                e,
                exc_info=True,
            )
            return {
                "status": "failed",
                "detail": f"Failed to load product photo: {e}",
            }

    best_attempt = await _generate_and_select_best_image(contents, image_prompt)

    if "status" in best_attempt and best_attempt["status"] == "failed":
        return best_attempt

    asset_sheet_filename = "asset_sheet.png"
    await tool_context.save_artifact(
        asset_sheet_filename,
        genai.types.Part.from_bytes(
            data=best_attempt["image_bytes"],
            mime_type=best_attempt["mime_type"],
        ),
    )
    logging.info("Saved asset sheet image to %s", asset_sheet_filename)

    return asset_sheet_filename


async def _save_json_artifact(
    tool_context: ToolContext,
    name: str,
    data: dict[str, str | None | dict | list],
) -> str:
    """Saves a JSON object as a text artifact.

    Args:
        tool_context (ToolContext): The context for saving artifacts.
        name (str): The base name for the artifact file.
        data (Dict[str, Union[Optional[str], dict, list]]): The
          JSON-serializable data to save.

    Returns:
        The filename of the saved artifact.
    """
    idx = int(time.time() * 1000) % 100
    filename = f"{name}_{idx}.json"
    json_data = json.dumps(data)
    part = genai.types.Part(text=json_data)
    await tool_context.save_artifact(filename, part)
    logging.info("Saved %s to artifacts as %s", name, filename)
    return filename
