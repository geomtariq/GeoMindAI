import sys
import os
import logging
import traceback

# Add backend/src to path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import settings

try:
    from services.ai_orchestrator import ai_orchestrator
    
    if ai_orchestrator:
        # Mock schema context
        if hasattr(ai_orchestrator, 'update_schema_context'):
            ai_orchestrator.update_schema_context({
                "tables": [{"name": "WELLS", "columns": [{"name": "WELL_NAME", "type": "VARCHAR2"}]}]
            })
        
        query = "update depth of MOCK WELL A to 1200, chnage status to inactive"
        
        # We need to monkeypatch the logger to capture the error
        original_error = logger.error
        def capture_error(msg, *args, **kwargs):
            with open("captured_error.txt", "w") as f:
                f.write(str(msg))
            original_error(msg, *args, **kwargs)
        
        # Patch the logger in the module
        import services.ai_orchestrator as ai_module
        ai_module.logger.error = capture_error
        
        result = ai_orchestrator.process_query(query)
        print(f"Result: {result}")
        
    else:
        with open("captured_error.txt", "w") as f:
            f.write("AI Orchestrator is None")

except Exception as e:
    with open("captured_error.txt", "w") as f:
        f.write(f"CRITICAL ERROR: {e}\n{traceback.format_exc()}")
