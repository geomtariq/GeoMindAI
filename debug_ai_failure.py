import sys
import os
import logging

# Add backend/src to path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import settings
print(f"API Key present: {bool(settings.GEMINI_API_KEY)}")

try:
    from services.ai_orchestrator import ai_orchestrator
    
    if ai_orchestrator:
        print("AI Orchestrator loaded successfully.")
        
        # Mock schema context since we aren't running the full app
        if hasattr(ai_orchestrator, 'update_schema_context'):
            ai_orchestrator.update_schema_context({
                "tables": [
                    {
                        "name": "WELLS",
                        "columns": [
                            {"name": "WELL_ID", "type": "NUMBER", "pk": True},
                            {"name": "WELL_NAME", "type": "VARCHAR2(100)"},
                            {"name": "DEPTH", "type": "NUMBER"},
                            {"name": "STATUS", "type": "VARCHAR2(20)"}
                        ]
                    }
                ]
            })
        
        query = "update depth of MOCK WELL A to 1200, chnage status to inactive"
        print(f"\nProcessing query: {query}")
        
        result = ai_orchestrator.process_query(query)
        print(f"\nResult: {result}")
    else:
        print("AI Orchestrator is None (failed to initialize).")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
