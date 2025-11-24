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
                file_path = os.path.join(backend_dir, '..', ref_file)
                
                if not os.path.exists(file_path):
                    logger.warning(f"Reference file not found: {file_path}")
                    continue
                
                logger.info(f"Parsing {ref_file}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
                # Split into sections
                sections = content.split('\n\n')
                
                current_category = "General"
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue
                    
                    # Check if this is a category header (numbered sections)
                    if section[0].isdigit() and '.' in section[:5]:
                        current_category = section.split('\n')[0]
                        continue
                    
                    # Extract SQL patterns (lines with SQL keywords)
                    lines = section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Check if line contains SQL keywords
                        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 
                                       'ALTER', 'DROP', 'JOIN', 'WHERE', 'GROUP BY', 
                                       'ORDER BY', 'HAVING', 'WITH', 'FROM']
                        
                        if any(keyword in line.upper() for keyword in sql_keywords):
                            entries.append({
                                'text': line,
                                'category': current_category,
                                'sql': line
                            })
            
            # Add some common patterns manually for better coverage
            common_patterns = [
                {
                    'text': 'Get all records from a table: SELECT * FROM table_name',
                    'category': 'Basic SELECT',
                    'sql': 'SELECT * FROM table_name'
                },
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
                    'text': 'Group and aggregate: SELECT column, COUNT(*) FROM table GROUP BY column',
                    'category': 'Aggregation',
                    'sql': 'SELECT column, COUNT(*) FROM table GROUP BY column'
                },
                {
                    'text': 'Update records: UPDATE table SET column = value WHERE condition',
                    'category': 'Update',
                    'sql': 'UPDATE table SET column = value WHERE condition'
                },
                {
                    'text': 'Insert new record: INSERT INTO table (col1, col2) VALUES (val1, val2)',
                    'category': 'Insert',
                    'sql': 'INSERT INTO table (col1, col2) VALUES (val1, val2)'
                },
                {
                    'text': 'Delete records: DELETE FROM table WHERE condition',
                    'category': 'Delete',
                    'sql': 'DELETE FROM table WHERE condition'
                },
                {
                    'text': 'Sum aggregation: SELECT SUM(column) FROM table',
                    'category': 'Aggregation',
                    'sql': 'SELECT SUM(column) FROM table'
                },
                {
                    'text': 'Average calculation: SELECT AVG(column) FROM table',
                    'category': 'Aggregation',
                    'sql': 'SELECT AVG(column) FROM table'
                },
                {
                    'text': 'Count records: SELECT COUNT(*) FROM table',
                    'category': 'Aggregation',
                    'sql': 'SELECT COUNT(*) FROM table'
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
