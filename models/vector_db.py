"""
Vector Database using Faiss for efficient similarity search
"""
import os
import json
import numpy as np
import faiss
from typing import List, Tuple, Dict


class VectorDatabase:
    """
    A class to manage vector embeddings using Faiss for efficient similarity search.
    """
    
    def __init__(self, embedding_dim: int, index_path: str, metadata_path: str):
        """
        Initialize the vector database.
        
        Args:
            embedding_dim: Dimension of the embedding vectors
            index_path: Path to save/load the Faiss index
            metadata_path: Path to save/load image metadata
        """
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.image_metadata = []  # List of {id, filename, path}
        
    def create_index(self):
        """
        Create a new Faiss index using Inner Product (for cosine similarity with normalized vectors)
        """
        # Using IndexFlatIP for inner product (cosine similarity when vectors are normalized)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        print(f"Created new Faiss index with dimension {self.embedding_dim}")
        
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict]):
        """
        Add vectors to the index along with their metadata.
        
        Args:
            vectors: Numpy array of shape (N, embedding_dim)
            metadata: List of dictionaries containing image metadata
        """
        if self.index is None:
            self.create_index()
            
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add to index
        self.index.add(vectors)
        
        # Add metadata
        self.image_metadata.extend(metadata)
        
        print(f"Added {len(vectors)} vectors to the index. Total vectors: {self.index.ntotal}")
        
    def search(self, query_vector: np.ndarray, top_k: int = 50) -> List[Dict]:
        """
        Search for similar vectors in the database.
        
        Args:
            query_vector: Query vector of shape (1, embedding_dim)
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing search results with metadata and similarity scores
        """
        if self.index is None or self.index.ntotal == 0:
            print("Warning: Index is empty or not loaded")
            return []
            
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # Search
        top_k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, top_k)
        
        # Prepare results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.image_metadata):
                result = self.image_metadata[idx].copy()
                result['similarity_score'] = float(dist)
                result['rank'] = i + 1
                results.append(result)
                
        return results
    
    def save(self):
        """
        Save the Faiss index and metadata to disk.
        """
        if self.index is None:
            print("Warning: No index to save")
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save Faiss index
        faiss.write_index(self.index, self.index_path)
        print(f"Saved Faiss index to {self.index_path}")
        
        # Save metadata
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.image_metadata, f, indent=2, ensure_ascii=False)
        print(f"Saved metadata to {self.metadata_path}")
        
    def load(self):
        """
        Load the Faiss index and metadata from disk.
        """
        if not os.path.exists(self.index_path):
            print(f"Index file not found at {self.index_path}")
            return False
            
        if not os.path.exists(self.metadata_path):
            print(f"Metadata file not found at {self.metadata_path}")
            return False
            
        # Load Faiss index
        self.index = faiss.read_index(self.index_path)
        print(f"Loaded Faiss index from {self.index_path} with {self.index.ntotal} vectors")
        
        # Load metadata
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.image_metadata = json.load(f)
        print(f"Loaded metadata with {len(self.image_metadata)} entries")
        
        return True
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector database.
        
        Returns:
            Dictionary containing database statistics
        """
        stats = {
            'total_vectors': self.index.ntotal if self.index else 0,
            'embedding_dim': self.embedding_dim,
            'metadata_entries': len(self.image_metadata),
            'index_loaded': self.index is not None
        }
        return stats
