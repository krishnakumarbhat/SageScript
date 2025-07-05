#!/usr/bin/env python3
"""
A script to analyze an image using a local Ollama LLaVA model.

This script takes a path to an image file as a command-line argument,
sends it to the specified local LLaVA model via the Ollama API,
and prints the model's description of the image.

Prerequisites:
1. Ollama must be installed and running on your local machine.
2. The required model must be pulled: `ollama pull llava:7b-v1.6-mistral-q3_K_M`
3. The ollama Python library must be installed: `pip install ollama`

Usage:
    python describe_image.py /path/to/your/image.jpg
"""
import sys
import os
import ollama

# --- Configuration ---
# The specific LLaVA model name you requested.
# The model ID '25a00600f8b4' is an internal hash, we use the model name to call it.
MODEL_NAME = "llava:7b-v1.6-mistral-q3_K_M"

def analyze_image(image_path: str):
    """
    Analyzes an image file using the specified LLaVA model and prints the description.

    Args:
        image_path (str): The full path to the image file.
    """
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at '{image_path}'")
        sys.exit(1)

    print(f"🖼️  Analyzing image: {os.path.basename(image_path)}")
    print(f"🤖 Using model: {MODEL_NAME}")
    print("--------------------------------------------------")

    try:
        # The 'images' parameter takes a list of file paths.
        # The library handles encoding the image for the API call.
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': 'Describe this image in detail. What is happening? What objects are present?',
                    'images': [image_path]
                }
            ]
        )

        print("\n✅ LLaVA's Description:")
        print(response['message']['content'])

    except ollama.ResponseError as e:
        print(f"❌ An error occurred with the Ollama API.")
        print(f"Error: {e.error}")
        if "model not found" in e.error:
            print(f"Please make sure you have pulled the model with: 'ollama pull {MODEL_NAME}'")
    except Exception as e:
        print(f"❌ An unexpected error occurred. Is the Ollama server running?")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """
    Main function to handle command-line arguments and start the analysis.
    """
    # Check if a command-line argument (the image path) was provided
    if len(sys.argv) < 2:
        print("❌ Error: No image path provided.")
        print(f"Usage: python {sys.argv[0]} <path_to_image_file>")
        sys.exit(1)

    # The image path is the first argument after the script name
    image_path = sys.argv[1]
    analyze_image(image_path)

if __name__ == "__main__":
    main()