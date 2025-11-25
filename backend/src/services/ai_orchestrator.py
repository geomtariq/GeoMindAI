import logging
from config import settings

logger = logging.getLogger(__name__)

# Try to use Gemini if API key is provided (regardless of USE_MOCK_DB)
# USE_MOCK_DB only affects the database, not the AI
ai_impl = None

if settings.GEMINI_API_KEY:
    try:
        from google import genai
        from services.sql_knowledge_base import sql_knowledge_base
        
        # Initialize knowledge base with user-specified comprehensive reference
        logger.info("Initializing SQL Knowledge Base...")
        # Add the specific absolute path requested by the user
        sql_knowledge_base.reference_files = [
            "sql_reference.txt", 
            r"D:\GeoMindAI\GeoMindAI\comprehensive_sql_reference.txt"
        ]
        sql_knowledge_base.initialize()
        
        class GeminiAIOrchestrator:
            def __init__(self):
                # Initialize the client with the API key
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.model_name = "gemini-2.0-flash" # Use the faster, newer model
                
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

Task: Convert the following natural language query into Oracle SQL based on the Database Schema provided above.

Rules:
1. Return ONLY the SQL statement, no explanations or markdown.
2. Use proper Oracle SQL syntax.
3. Analyze the "Database Schema" section above to find the correct table and column names.
4. For INSERT operations, check the schema for all columns that are NOT NULL or required, and try to map user input to them.
5. Do NOT make up column names. Only use columns explicitly listed in the Schema.
6. TRANSFORM all string literal values to UPPERCASE, even if the user types them in lowercase (e.g. 'lora' -> 'LORA', 'active' -> 'ACTIVE'). This is CRITICAL for data consistency.
7. For UPDATE/DELETE operations, use WHERE clauses to target specific records.
8. If the user asks for multiple distinct actions (e.g. "create well AND create table"), return multiple SQL statements separated by a semicolon (;).

Examples (General Patterns):
- "create new [entity] with [attributes]" → INSERT INTO [TABLE] (COL1, COL2...) VALUES (VAL1, VAL2...)
- "add well named lora with status active" → INSERT INTO WELLS (WELL_NAME, STATUS) VALUES ('LORA', 'ACTIVE')
- "update [entity] [field] to [value]" → UPDATE [TABLE] SET [COL] = [VAL] WHERE [ID_COL] = ...
- "show all [entities]" → SELECT * FROM [TABLE]
- "create well A and add child table B" → INSERT INTO WELLS ...; CREATE TABLE B ...

Natural Language Query: {query}

SQL:"""
                    
                    # Generate SQL using the new client
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                    sql = response.text.strip()
                    
                    # Remove markdown code blocks if present
                    if sql.startswith('```'):
                        lines = sql.split('\n')
                        sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql
                        sql = sql.replace('```sql', '').replace('```', '')
                    sql = sql.strip()
                    
                    # Remove any trailing semicolons (only if single statement, but we allow multiple now)
                    # Actually, we should keep internal semicolons but maybe remove the very last one
                    if sql.endswith(';'):
                        sql = sql[:-1]
                    
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
        logger.info("✅ Using Gemini AI Orchestrator (v2 SDK) with RAG and Dynamic Schema")
        
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