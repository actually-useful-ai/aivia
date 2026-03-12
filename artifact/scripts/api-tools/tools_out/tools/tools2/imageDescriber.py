from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os

# Define the main tool class
class ImageDescriber:
    def __init__(self):
        # Load the BLIP model and processor
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

    def describe_image(self, image_path):
        try:
            # Open and process the image
            image = Image.open(image_path)
            inputs = self.processor(images=image, return_tensors="pt")
            
            # Generate description (caption) for the image
            caption = self.model.generate(**inputs)
            description = self.processor.decode(caption[0], skip_special_tokens=True)
            return description
        except Exception as e:
            return f"Error processing image: {str(e)}"

# Define the entry point for the tool
def main(image_path):
    tool = ImageDescriber()
    description = tool.describe_image(image_path)
    return {"description": description}

