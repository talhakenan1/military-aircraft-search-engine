"""
Script to create embeddings for airplane images using CLIP model
"""
import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models import VectorDatabase


class EmbeddingGenerator:
    """
    Generate embeddings for images using CLIP model
    """
    
    def __init__(self):
        """
        Initialize the embedding generator with CLIP model
        """
        print(f"Initializing CLIP model: {config.CLIP_MODEL_NAME}")
        print(f"Using device: {config.DEVICE}")
        
        # Load CLIP model and processor
        self.model = CLIPModel.from_pretrained(config.CLIP_MODEL_NAME).to(config.DEVICE)
        self.processor = CLIPProcessor.from_pretrained(config.CLIP_MODEL_NAME)
        self.model.eval()  # Set to evaluation mode
        
        print("Model loaded successfully!")
        
    def load_image(self, image_path: str) -> Image.Image:
        """
        Load and preprocess an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
        """
        try:
            image = Image.open(image_path).convert('RGB')
            # Resize if image is too large
            if image.size[0] > config.MAX_IMAGE_SIZE[0] or image.size[1] > config.MAX_IMAGE_SIZE[1]:
                image.thumbnail(config.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def generate_embedding(self, image: Image.Image) -> np.ndarray:
        """
        Generate embedding for a single image
        
        Args:
            image: PIL Image object
            
        Returns:
            Numpy array of embedding vector
        """
        with torch.no_grad():
            inputs = self.processor(images=image, return_tensors="pt").to(config.DEVICE)
            image_features = self.model.get_image_features(**inputs)
            
            # Convert to numpy and normalize
            embedding = image_features.cpu().numpy().flatten()
            
        return embedding
    
    def generate_embeddings_batch(self, images: list) -> np.ndarray:
        """
        Generate embeddings for a batch of images
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Numpy array of shape (batch_size, embedding_dim)
        """
        with torch.no_grad():
            inputs = self.processor(images=images, return_tensors="pt", padding=True).to(config.DEVICE)
            image_features = self.model.get_image_features(**inputs)
            
            # Convert to numpy
            embeddings = image_features.cpu().numpy()
            
        return embeddings
    
    def process_directory(self, images_dir: str, output_db: VectorDatabase):
        """
        Process all images in a directory and create embeddings
        
        Args:
            images_dir: Directory containing images
            output_db: VectorDatabase instance to store embeddings
        """
        # Get all image files
        image_files = []
        for ext in config.ALLOWED_EXTENSIONS:
            image_files.extend(Path(images_dir).rglob(f"*{ext}"))
            image_files.extend(Path(images_dir).rglob(f"*{ext.upper()}"))
        
        image_files = sorted(list(set(image_files)))  # Remove duplicates
        
        if not image_files:
            print(f"No images found in {images_dir}")
            print(f"Supported extensions: {config.ALLOWED_EXTENSIONS}")
            return
        
        print(f"Found {len(image_files)} images")
        
        # Process images in batches
        batch_images = []
        batch_metadata = []
        
        for img_path in tqdm(image_files, desc="Processing images"):
            # Load image
            image = self.load_image(str(img_path))
            if image is None:
                continue
            
            # Add to batch
            batch_images.append(image)
            batch_metadata.append({
                'id': len(batch_metadata),
                'filename': img_path.name,
                'path': str(img_path.relative_to(images_dir))
            })
            
            # Process batch when it's full
            if len(batch_images) >= config.BATCH_SIZE:
                embeddings = self.generate_embeddings_batch(batch_images)
                output_db.add_vectors(embeddings, batch_metadata)
                
                # Reset batch
                batch_images = []
                batch_metadata = []
        
        # Process remaining images
        if batch_images:
            embeddings = self.generate_embeddings_batch(batch_images)
            output_db.add_vectors(embeddings, batch_metadata)
        
        print(f"\nProcessing complete!")
        print(f"Total embeddings created: {output_db.get_stats()['total_vectors']}")


def main():
    """
    Main function to run the embedding generation process
    """
    print("=" * 60)
    print("Airplane Search Engine - Embedding Generation")
    print("=" * 60)
    print()
    
    # Check if images directory exists
    if not os.path.exists(config.AIRPLANE_PHOTOS_DIR):
        print(f"Error: Images directory not found at {config.AIRPLANE_PHOTOS_DIR}")
        print("Please place your airplane photos in the 'data/airplane_photos' directory")
        return
    
    # Initialize embedding generator
    generator = EmbeddingGenerator()
    
    # Initialize vector database
    vector_db = VectorDatabase(
        embedding_dim=config.EMBEDDING_DIM,
        index_path=config.FAISS_INDEX_PATH,
        metadata_path=config.IMAGE_METADATA_PATH
    )
    
    # Process all images
    generator.process_directory(config.AIRPLANE_PHOTOS_DIR, vector_db)
    
    # Save the database
    print("\nSaving vector database...")
    vector_db.save()
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Database Statistics:")
    stats = vector_db.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("=" * 60)
    print("\nEmbedding generation complete!")
    print(f"Index saved to: {config.FAISS_INDEX_PATH}")
    print(f"Metadata saved to: {config.IMAGE_METADATA_PATH}")


if __name__ == "__main__":
    main()
