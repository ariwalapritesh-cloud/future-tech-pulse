import logging
import os
import io
from PIL import Image
from google import genai
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

class VisualGenerator:
    def __init__(self):
        logger.info("Initializing Imagen 3 VisualGenerator...")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
        self.client = genai.Client(api_key=self.api_key)

    def generate_scene_image(self, prompt: str, output_filename: str):
        """
        Generates a 9:16 image using Imagen 3 based on the scene description.
        """
        output_path = settings.VISUALS_DIR / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating image for {output_filename}...")
        try:
            result = self.client.models.generate_images(
                model='imagen-3.0-generate-001',
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/jpeg",
                    person_generation="ALLOW_ADULT"
                )
            )
            
            for generated_image in result.generated_images:
                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                image.save(output_path)
                logger.info(f"Saved generated image to {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            # Fallback to a solid color if generation fails
            fallback = Image.new('RGB', (1080, 1920), color=(10, 10, 20))
            fallback.save(output_path)
            logger.warning(f"Saved fallback blank image to {output_path}")
            return output_path
