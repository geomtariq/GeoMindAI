import logging
from config import settings

logger = logging.getLogger(__name__)

# Try to use Gemini if API key is provided (regardless of USE_MOCK_DB)
# USE_MOCK_DB only affects the database, not the AI
ai_impl = None

if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        
        # Test the API key by configuring it
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        class GeminiAIOrchestrator:
            def __init__(self):
                self.model = genai.GenerativeModel('gemini-pro')
                
                # Database schema for context
                self.schema = """
                Database Schema:
                
                Table: WELLS
                Columns:
                - WELL_ID (NUMBER) - Primary key
                - WELL_NAME (VARCHAR2) - Well name
                - DEPTH (NUMBER) - Well depth in meters
                - STATUS (VARCHAR2) - Well status (ACTIVE, INACTIVE, etc.)
                
                Table: PRODUCTION
                Columns:
                - WELL_ID (NUMBER) - Foreign key to WELLS
                - DATE (DATE) - Production date
                - VOLUME (NUMBER) - Production volume
                """
            
            def process_query(self, query: str) -> dict:
                """
                Takes a natural language query and returns a dictionary with the SQL statement and intent.
                """
                try:
                    # Create prompt for SQL generation
                    prompt = f"""{self.schema}

Task: Convert the following natural language query into Oracle SQL.

Rules:
1. Return ONLY the SQL statement, no explanations
2. Use proper Oracle SQL syntax
3. For updates/deletes, use WHERE clauses to target specific records
4. Use partial name matching where appropriate (e.g., 'B' matches 'MOCK WELL B')

Natural Language Query: {query}

SQL:"""
                    
                    # Generate SQL
                    response = self.model.generate_content(prompt)
                    sql = response.text.strip()
                    
                    # Remove markdown code blocks if present
                    if sql.startswith('```'):
                        sql = sql.split('\n', 1)[1]
                        sql = sql.rsplit('```', 1)[0]
                    sql = sql.strip()
                    
                    # Determine intent based on SQL command
                    sql_upper = sql.upper()
                    if any(cmd in sql_upper for cmd in ['UPDATE', 'DELETE', 'INSERT', 'ALTER', 'DROP', 'CREATE']):
                        intent = 'write'
                    else:
                        intent = 'read'
                    
                    logger.info(f"Gemini generated SQL: {sql}, Intent: {intent}")
                    return {"intent": intent, "sql": sql}
                    
                except Exception as e:
                    logger.error(f"Gemini API error during query processing: {e}")
                    # Fall back to mock AI for this query
                    logger.warning("Falling back to Mock AI for this query")
                    from services.mock_ai_orchestrator import mock_ai_orchestrator
                    return mock_ai_orchestrator.process_query(query)
        
        # Try to create an instance to verify the API key works
        ai_impl = GeminiAIOrchestrator()
        logger.info("✅ Using Gemini AI Orchestrator")
        
    except Exception as e:
        logger.warning(f"❌ Failed to initialize Gemini AI Orchestrator: {e}")
        logger.info("Falling back to Mock AI Orchestrator")
        ai_impl = None

# Fall back to mock AI if Gemini failed or no API key
if ai_impl is None:
    from services.mock_ai_orchestrator import mock_ai_orchestrator as ai_impl
    logger.info("Using Mock AI Orchestrator (no valid Gemini API key)")

# Export the instance
ai_orchestrator = ai_impl