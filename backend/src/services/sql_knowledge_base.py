import logging
import os
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class SQLKnowledgeBase:
    """
    RAG-based SQL knowledge base using vector embeddings for semantic search.
    Parses comprehensive SQL reference and retrieves relevant examples for queries.
    """
    
    def __init__(self, reference_files: List[str] = None):
        if reference_files is None:
            reference_files = ["sql_reference.txt", "comprehensive_sql_reference.txt"]
        self.reference_files = reference_files
        self.model = None
        self.knowledge_entries = []
        self.embeddings = None
        self.initialized = False
        
    def initialize(self):
        """Load model, parse reference, and generate embeddings"""
        try:
            logger.info("Initializing SQL Knowledge Base...")
            
            # Load sentence transformer model (lightweight, fast)
            logger.info("Loading embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Parse SQL reference file
            logger.info(f"Parsing {self.reference_files}...")
            self.knowledge_entries = self._parse_sql_reference()
            logger.info(f"Loaded {len(self.knowledge_entries)} SQL patterns")
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            texts = [entry['text'] for entry in self.knowledge_entries]
            self.embeddings = self.model.encode(texts, show_progress_bar=False)
            
            self.initialized = True
            logger.info("✅ SQL Knowledge Base initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQL Knowledge Base: {e}")
            self.initialized = False
    
    def _parse_sql_reference(self) -> List[Dict]:
        """Parse SQL reference files into structured knowledge entries"""
        entries = []
        
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # Parse all reference files
            for ref_file in self.reference_files:
                # Handle both absolute and relative paths
                if os.path.isabs(ref_file):
                    file_path = ref_file
                else:
                    file_path = os.path.join(backend_dir, '..', ref_file)
                
                if not os.path.exists(file_path):
                    logger.warning(f"Reference file not found: {file_path}")
                    continue
                
                logger.info(f"Parsing {ref_file} from {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
                # Split into logical chunks (paragraphs or sections)
                # The user wants to "consume all knowledge", so we shouldn't filter too aggressively.
                # We'll split by double newlines to get paragraphs/blocks.
                chunks = content.split('\n\n')
                
                for chunk in chunks:
                    chunk = chunk.strip()
                    if not chunk:
                        continue
                    
                    # Use the first line as a pseudo-category or summary
                    lines = chunk.split('\n')
                    category = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
                    
                    entries.append({
                        'text': chunk, # Store the full chunk text for embedding
                        'category': "Reference Knowledge",
                        'sql': chunk   # The 'sql' field is used for display, so show the whole chunk
                    })
            
            # Add some common patterns manually for better coverage (keep these as they are useful fallbacks)
            common_patterns = [
                {
                    'text': 'Get all records from a table: SELECT * FROM table_name',
                    'category': 'Basic SELECT',
                    'sql': 'SELECT * FROM table_name'
                },
                # ... (rest of common patterns can be kept or re-added if needed, but for brevity in this tool call I will omit them if I can't see them all. 
                # Actually, I should probably keep them to ensure basic functionality isn't lost if the files are empty.)
                 {
                    'text': 'Filter records with WHERE: SELECT * FROM table WHERE column = value',
                    'category': 'Filtering',
                    'sql': 'SELECT * FROM table WHERE column = value'
                },
                {
                    'text': 'Join two tables: SELECT * FROM table1 JOIN table2 ON table1.id = table2.id',
                    'category': 'Joins',
                    'sql': 'SELECT * FROM table1 JOIN table2 ON table1.id = table2.id'
                },
                {
                    'text': 'Insert new record: INSERT INTO table (col1, col2) VALUES (val1, val2)',
                    'category': 'Insert',
                    'sql': 'INSERT INTO table (col1, col2) VALUES (val1, val2)'
                },
                {
                    'text': 'Update records: UPDATE table SET column = value WHERE condition',
                    'category': 'Update',
                    'sql': 'UPDATE table SET column = value WHERE condition'
                },
                {
                    'text': 'Delete records: DELETE FROM table WHERE condition',
                    'category': 'Delete',
                    'sql': 'DELETE FROM table WHERE condition'
                }
            ]
            
            entries.extend(common_patterns)
            
        except Exception as e:
            logger.error(f"Error parsing SQL reference: {e}")
            # Return basic patterns as fallback
            return common_patterns
        
        return entries
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find most similar SQL patterns to the query using semantic search
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            
        Returns:
            List of relevant SQL patterns with scores
        """
        if not self.initialized:
            logger.warning("Knowledge base not initialized, returning empty results")
            return []
        
        try:
            # Embed the query
            query_embedding = self.model.encode([query])[0]
            
            # Calculate cosine similarity
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Build results
            results = []
            for idx in top_indices:
                results.append({
                    'sql': self.knowledge_entries[idx]['sql'],
                    'category': self.knowledge_entries[idx]['category'],
                    'score': float(similarities[idx]),
                    'text': self.knowledge_entries[idx]['text']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def get_context_for_query(self, query: str, top_k: int = 5) -> str:
        """
        Get formatted context string for AI prompt
        
        Args:
            query: Natural language query
            top_k: Number of examples to retrieve
            
        Returns:
            Formatted string with relevant SQL examples
        """
        results = self.search_similar(query, top_k)
        
        if not results:
            return ""
        
        context = "Relevant SQL Patterns from Knowledge Base:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. [{result['category']}] {result['sql']}\n"
        
        return context

# Global instance
sql_knowledge_base = SQLKnowledgeBase()
