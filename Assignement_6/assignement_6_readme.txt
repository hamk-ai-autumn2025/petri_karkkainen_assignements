# Generate 2 square images with default settings
python hf_image_generator.py "a magical forest" --token $HF_TOKEN

# Generate 4 landscape images with negative prompt
python hf_image_generator.py "cyberpunk city" --negative-prompt "blurry, low quality" --aspect Landscape --count 4 --token $HF_TOKEN

# Generate 1 image with specific seed
python hf_image_generator.py "mountain landscape" --seed 42 --aspect Custom --width 768 --height 512 --token $HF_TOKEN



