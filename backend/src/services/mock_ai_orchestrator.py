import logging
import re

logger = logging.getLogger(__name__)

class MockAIOrchestrator:
    def process_query(self, query: str) -> dict:
        """
        Mocks processing a natural language query.
        Returns hardcoded SQL and intent based on regex patterns.
        """
        logger.info(f"[MOCK AI] Processing query: {query}")
        
        query_lower = query.lower()
        
        # Pattern 1: Update Well Depth
        # "change well 1 depth to 2000" or "update well A depth to 500"
        update_match = re.search(r"(?:change|update|set|edit|modify)\s+well\s+(.+?)\s+depth\s+to\s+(\d+)", query_lower)
        
        # Pattern 1a: Alternative Phrasing for Depth
        # "edit depth of well B to 1200"
        if not update_match:
            update_match = re.search(r"(?:change|update|set|edit|modify)\s+depth\s+of\s+well\s+(.+?)\s+to\s+(\d+)", query_lower)

        if update_match:
            well_identifier = update_match.group(1).strip()
            new_depth = update_match.group(2)
            
            # Check if identifier is numeric (ID) or string (Name)
            if well_identifier.isdigit():
                where_clause = f"WELL_ID = {well_identifier}"
            else:
                where_clause = f"WELL_NAME = '{well_identifier.upper()}'"
                
            return {
                "intent": "write",
                "sql": f"UPDATE WELLS SET DEPTH = {new_depth} WHERE {where_clause}"
            }

        # Pattern 1b: Update Well Status
        # "change status of well B to inactive" or "change well B status to inactive"
        status_match = re.search(r"(?:change|update|set|edit|modify)\s+status\s+of\s+well\s+(.+?)\s+to\s+(\w+)", query_lower)
        if not status_match:
            status_match = re.search(r"(?:change|update|set|edit|modify)\s+well\s+(.+?)\s+status\s+to\s+(\w+)", query_lower)
            
        if status_match:
            well_identifier = status_match.group(1).strip()
            new_status = status_match.group(2).upper()
            
            if well_identifier.isdigit():
                where_clause = f"WELL_ID = {well_identifier}"
            else:
                where_clause = f"WELL_NAME = '{well_identifier.upper()}'"
                
            return {
                "intent": "write",
                "sql": f"UPDATE WELLS SET STATUS = '{new_status}' WHERE {where_clause}"
            }

        # Pattern 1c: Partial Update (Missing Identifier)
        # "edit well depth to 3000" or "change status of well to inactive"
        if re.search(r"(?:change|update|set|edit|modify)\s+well\s+depth", query_lower):
             return {
                "intent": "read",
                "sql": "SELECT 'Error: Please specify which well to update (e.g., edit well A depth to 3000)' FROM DUAL"
            }
        if re.search(r"(?:change|update|set|edit|modify)\s+(?:status\s+of\s+)?well\s+(?:status\s+)?to\s+\w+", query_lower):
             return {
                "intent": "read",
                "sql": "SELECT 'Error: Please specify which well to update (e.g., change status of well A to inactive)' FROM DUAL"
            }

        # Pattern 2: Count Wells
        # "how many wells" or "count wells"
        if "how many" in query_lower or "count" in query_lower:
            if "well" in query_lower:
                return {
                    "intent": "read",
                    "sql": "SELECT COUNT(*) FROM WELLS"
                }

        # Pattern 3: Select Specific Well
        # "show well 1" or "get well A" or "show the well B"
        select_match = re.search(r"(?:show|get|find)\s+(?:the\s+)?well\s+(.+)", query_lower)
        if select_match:
            well_identifier = select_match.group(1).strip()
            if well_identifier.isdigit():
                 where_clause = f"WELL_ID = {well_identifier}"
            else:
                 where_clause = f"WELL_NAME = '{well_identifier.upper()}'"
            
            return {
                "intent": "read",
                "sql": f"SELECT * FROM WELLS WHERE {where_clause}"
            }

        # Pattern 4: General Selects (Fallback for keywords)
        if "well" in query_lower:
            return {
                "intent": "read",
                "sql": "SELECT * FROM WELLS"
            }
        elif "production" in query_lower:
            return {
                "intent": "read",
                "sql": "SELECT * FROM PRODUCTION"
            }
        
        # Default fallback
        return {
            "intent": "read",
            "sql": "SELECT 'I did not understand that query. Try: Show wells, How many wells, or Edit well A depth to 3000' FROM DUAL"
        }

mock_ai_orchestrator = MockAIOrchestrator()
