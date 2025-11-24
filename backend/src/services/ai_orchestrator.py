import logging
from config import settings

logger = logging.getLogger(__name__)

# Try to use Gemini if API key is provided (regardless of USE_MOCK_DB)
# USE_MOCK_DB only affects the database, not the AI
ai_impl = None

if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        from services.sql_knowledge_base import sql_knowledge_base
        
        # Test the API key by configuring it
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize knowledge base
        logger.info("Initializing SQL Knowledge Base...")
        sql_knowledge_base.initialize()
        
        class GeminiAIOrchestrator:
            def __init__(self):
                self.model = genai.GenerativeModel('gemini-pro')
                
                # Default schema (will be updated dynamically on connection)
                self.schema = "Database Schema: Not connected. Please connect to a database."
            
            def update_schema_context(self, metadata: dict):
                """
                Update the schema context from discovered database metadata.
                """
                try:
                    schema_text = "Database Schema (Discovered):\n\n"
                    
                    for table in metadata.get("tables", []):
                        schema_text += f"Table: {table['name']}\nColumns:\n"
                        for col in table.get("columns", []):
                            constraints = col.get("constraints", "")
                            if col.get("pk"):
                                constraints += " PRIMARY KEY"
                            if col.get("fk"):
                                constraints += f" FOREIGN KEY -> {col['fk']}"
                            
                            schema_text += f"- {col['name']} ({col['type']}) {constraints}\n"
                        schema_text += "\n"
                    
                    self.schema = schema_text
                    logger.info("✅ AI Schema context updated dynamically")
                except Exception as e:
                    logger.error(f"Failed to update schema context: {e}")
            
            def process_query(self, query: str) -> dict:
                """
                Takes a natural language query and returns a dictionary with the SQL statement and intent.
                Uses RAG to retrieve relevant SQL examples from knowledge base.
                """
                try:
                    # Retrieve relevant SQL examples from knowledge base
                    relevant_context = ""
                    if sql_knowledge_base.initialized:
                        relevant_context = sql_knowledge_base.get_context_for_query(query, top_k=5)
                        logger.info("Retrieved relevant SQL patterns from knowledge base")
                    
                    # Create comprehensive prompt for SQL generation with RAG context
                    prompt = f"""{self.schema}

{relevant_context}

Task: Convert the following natural language query into Oracle SQL.

Rules:
1. Return ONLY the SQL statement, no explanations or markdown
2. Use proper Oracle SQL syntax
3. For INSERT operations, include all required columns (WELL_NAME, STATUS, DEPTH for WELLS)
4. For UPDATE/DELETE operations, ALWAYS use WHERE clauses to target specific records
- "update well a name to TARIQ" → UPDATE WELLS SET WELL_NAME = 'TARIQ' WHERE WELL_NAME LIKE '%A%'
- "change well B name to NEWNAME" → UPDATE WELLS SET WELL_NAME = 'NEWNAME' WHERE WELL_NAME LIKE '%B%'
- "rename well C to CHARLIE" → UPDATE WELLS SET WELL_NAME = 'CHARLIE' WHERE WELL_NAME LIKE '%C%'
- "set well A status to INACTIVE" → UPDATE WELLS SET STATUS = 'INACTIVE' WHERE WELL_NAME LIKE '%A%'
- "delete well tariq" → DELETE FROM WELLS WHERE WELL_NAME LIKE '%TARIQ%'
- "show production for well A" → SELECT P.* FROM PRODUCTION P JOIN WELLS W ON P.WELL_ID = W.WELL_ID WHERE W.WELL_NAME LIKE '%A%'
- "count active wells" → SELECT COUNT(*) FROM WELLS WHERE STATUS = 'ACTIVE'
- "average depth by status" → SELECT STATUS, AVG(DEPTH) FROM WELLS GROUP BY STATUS

Natural Language Query: {query}

SQL:"""
                    
                    # Generate SQL
                    response = self.model.generate_content(prompt)
                    sql = response.text.strip()
                    
                    # Remove markdown code blocks if present
                    if sql.startswith('```'):
                        lines = sql.split('\n')
                        sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql
                        sql = sql.replace('```sql', '').replace('```', '')
                    sql = sql.strip()
                    
                    # Remove any trailing semicolons
                    sql = sql.rstrip(';')
                    
                    # Determine intent based on SQL command
                    sql_upper = sql.upper()
                    if any(cmd in sql_upper for cmd in ['UPDATE', 'DELETE', 'INSERT', 'ALTER', 'DROP', 'CREATE', 'TRUNCATE']):
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
        logger.info("✅ Using Gemini AI Orchestrator with RAG and Dynamic Schema")
        
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