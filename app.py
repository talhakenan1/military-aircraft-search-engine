"""
Flask application for Airplane Search Engine
"""
import os
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
from transformers import CLIPProcessor, CLIPModel

import config
from models import VectorDatabase


app = Flask(__name__)
CORS(app)

# Global variables for model and database
clip_model = None
clip_processor = None
vector_db = None


def initialize_app():
    """
    Initialize the CLIP model and vector database
    """
    global clip_model, clip_processor, vector_db
    
    print("=" * 60)
    print("Initializing Airplane Search Engine...")
    print("=" * 60)
    
    # Load CLIP model
    print(f"Loading CLIP model: {config.CLIP_MODEL_NAME}")
    print(f"Using device: {config.DEVICE}")
    clip_model = CLIPModel.from_pretrained(config.CLIP_MODEL_NAME).to(config.DEVICE)
    clip_processor = CLIPProcessor.from_pretrained(config.CLIP_MODEL_NAME)
    clip_model.eval()
    print("✓ CLIP model loaded successfully")
    
    # Load vector database
    print("\nLoading vector database...")
    vector_db = VectorDatabase(
        embedding_dim=config.EMBEDDING_DIM,
        index_path=config.FAISS_INDEX_PATH,
        metadata_path=config.IMAGE_METADATA_PATH
    )
    
    if vector_db.load():
        stats = vector_db.get_stats()
        print(f"✓ Vector database loaded successfully")
        print(f"  Total images indexed: {stats['total_vectors']}")
    else:
        print("✗ Failed to load vector database")
        print("Please run 'python scripts/create_embeddings.py' first to create the index")
        return False
    
    print("=" * 60)
    print("Initialization complete!")
    print("=" * 60)
    return True


def generate_text_embedding(text: str) -> np.ndarray:
    """
    Generate embedding for text query using CLIP
    
    Args:
        text: Search query text
        
    Returns:
        Numpy array of embedding vector
    """
    with torch.no_grad():
        inputs = clip_processor(text=[text], return_tensors="pt", padding=True).to(config.DEVICE)
        text_features = clip_model.get_text_features(**inputs)
        embedding = text_features.cpu().numpy().flatten()
    
    return embedding


@app.route('/')
def index():
    """
    Render the main search page
    """
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """
    Search endpoint for text-to-image search
    
    Expected JSON body:
    {
        "query": "search text",
        "top_k": 50  (optional, default from config)
    }
    
    Returns:
    {
        "success": true/false,
        "query": "search text",
        "results": [...],
        "total_results": N,
        "message": "error message if failed"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing query parameter'
            }), 400
        
        query_text = data['query'].strip()
        
        if not query_text:
            return jsonify({
                'success': False,
                'message': 'Query cannot be empty'
            }), 400
        
        # Get top_k parameter (default from config)
        top_k = data.get('top_k', config.DEFAULT_TOP_K)
        top_k = min(top_k, config.MAX_TOP_K)  # Enforce maximum
        
        # Generate text embedding
        query_embedding = generate_text_embedding(query_text)
        
        # Search in vector database
        results = vector_db.search(query_embedding, top_k=top_k)
        
        # Format results for response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result['id'],
                'filename': result['filename'],
                'path': result['path'],
                'similarity_score': round(result['similarity_score'], 4),
                'rank': result['rank'],
                'image_url': f"/api/image/{result['path']}"
            })
        
        return jsonify({
            'success': True,
            'query': query_text,
            'results': formatted_results,
            'total_results': len(formatted_results)
        })
        
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'Search failed: {str(e)}'
        }), 500


@app.route('/api/image/<path:image_path>')
def serve_image(image_path):
    """
    Serve image files from the airplane photos directory
    
    Args:
        image_path: Relative path to the image
    """
    try:
        return send_from_directory(config.AIRPLANE_PHOTOS_DIR, image_path)
    except Exception as e:
        print(f"Error serving image {image_path}: {e}")
        return jsonify({'error': 'Image not found'}), 404


@app.route('/api/stats')
def get_stats():
    """
    Get statistics about the vector database
    
    Returns:
    {
        "success": true,
        "stats": {...}
    }
    """
    try:
        stats = vector_db.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """
    Handle 404 errors
    """
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """
    Handle 500 errors
    """
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize the application
    if initialize_app():
        # Run the Flask app
        print(f"\nStarting Flask server on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
        print("Press Ctrl+C to stop the server\n")
        
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
    else:
        print("\nFailed to initialize application. Exiting...")
