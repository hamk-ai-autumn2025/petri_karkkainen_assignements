#!/usr/bin/env python3
import requests
import time
import os
from urllib.parse import urlparse
import argparse
import base64
import io
from PIL import Image

def get_image_from_hf_spaces(prompt, negative_prompt=None, seed=None, width=512, height=512, api_token=None):
    """Generate image using Hugging Face Inference API with authentication"""
    # Using Stable Diffusion XL through Hugging Face Inference API (more reliable)
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    # Use provided token or environment variable
    token = api_token or os.getenv("HF_TOKEN")
    if not token:
        raise Exception("No API token provided. Set HF_TOKEN environment variable or use --token argument")

    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "inputs": prompt,
        "options": {
            "wait_for_model": True
        }
    }

    # Add negative prompt if provided
    if negative_prompt:
        if "parameters" not in payload:
            payload["parameters"] = {}
        payload["parameters"]["negative_prompt"] = negative_prompt

    # Add seed if provided
    if seed is not None:
        if "parameters" not in payload:
            payload["parameters"] = {}
        payload["parameters"]["seed"] = seed

    # Add image dimensions
    if "parameters" not in payload:
        payload["parameters"] = {}
    payload["parameters"]["width"] = width
    payload["parameters"]["height"] = height

    response = requests.post(api_url, headers=headers, json=payload)

    # Handle model loading
    if response.status_code == 503:
        print("Model is loading, please wait...")
        # Wait and retry
        time.sleep(20)  # Longer wait for larger models
        response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    return response.content

def download_images_from_hf(prompts, negative_prompts, seeds, width, height, api_token=None):
    """Generate and download images from Hugging Face"""
    filenames = []
    timestamp = int(time.time())

    for i, (prompt, neg_prompt, seed) in enumerate(zip(prompts, negative_prompts, seeds)):
        try:
            image_data = get_image_from_hf_spaces(prompt, neg_prompt, seed, width, height, api_token)

            # Save image with timestamped filename
            filename = f"image_{timestamp}_{i+1}.png"
            with open(filename, 'wb') as f:
                f.write(image_data)

            filenames.append(filename)
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Failed to generate image {i+1}: {e}")

    return filenames

def main():
    parser = argparse.ArgumentParser(description="Generate images using Hugging Face Spaces")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--negative-prompt", default="", help="Negative prompt to avoid certain elements")
    parser.add_argument("--seed", type=int, help="Seed for reproducible results")
    parser.add_argument("--aspect", default="Square",
                        choices=["Square", "Portrait", "Landscape", "Custom"],
                        help="Aspect ratio (default: Square)")
    parser.add_argument("--width", type=int, default=768, help="Image width (for Custom aspect)")
    parser.add_argument("--height", type=int, default=768, help="Image height (for Custom aspect)")
    parser.add_argument("--count", type=int, choices=[1, 2, 4, 6, 8], default=2,
                        help="Number of images to generate (1, 2, 4, 6, or 8)")
    parser.add_argument("--token", help="Hugging Face API token (alternative to HF_TOKEN env var)")

    args = parser.parse_args()

    # Check for token in environment variable if not provided as argument
    if not args.token and not os.getenv("HF_TOKEN"):
        print("Error: No API token provided.")
        print("Either set HF_TOKEN environment variable or use --token argument")
        return

    # Map aspect ratios to dimensions
    aspect_ratios = {
        "Square": (768, 768),
        "Portrait": (768, 1024),
        "Landscape": (1024, 768),
        "Custom": (args.width, args.height)
    }

    width, height = aspect_ratios[args.aspect]

    # Create lists for batch processing
    prompts = [args.prompt] * args.count
    negative_prompts = [args.negative_prompt] * args.count
    seeds = []

    if args.seed is not None:
        # Generate different seeds if not specified
        seeds = [args.seed + i for i in range(args.count)]
    else:
        # Use random seeds
        import random
        seeds = [random.randint(0, 2**32 - 1) for _ in range(args.count)]

    try:
        print(f"\nGenerating {args.count} image(s) with:")
        print(f"- Prompt: {args.prompt}")
        print(f"- Negative Prompt: {args.negative_prompt}")
        print(f"- Aspect: {args.aspect} ({width}x{height})")
        print(f"- Seeds: {seeds}")

        # Ask for confirmation
        download = input(f"\nProceed with generation? (y/n): ").lower()
        if download in ['y', 'yes']:
            filenames = download_images_from_hf(prompts, negative_prompts, seeds, width, height, args.token)
            print("\nSaved files:")
            for filename in filenames:
                print(f"- {filename}")
        else:
            print("Generation cancelled.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
