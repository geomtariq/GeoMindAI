import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

print("Attempting to import ai_orchestrator...")
try:
    from services.ai_orchestrator import ai_orchestrator
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
