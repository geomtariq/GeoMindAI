import logging
import re

logger = logging.getLogger(__name__)

class MockAIOrchestrator:
    def update_schema_context(self, metadata: dict):
        """
        Mock implementation of schema update.
        """
        logger.info("[MOCK AI] Schema context updated (mock)")

    def process_query(self, query: str) -> dict:
        """
        Mocks processing a natural language query.
        Returns hardcoded SQL and intent based on regex patterns.
        """
        logger.info(f"[MOCK AI] Processing query: {query}")
        
        query_lower = query.lower()
        
        # Pattern 0: Create/Insert New Well with Full Details (comma-separated or not)
        # "create new well with name TARIQ, depth 3000, status INACTIVE"
        full_create_match = re.search(
            r"(?:create|insert|add).*?name\s+([^,]+).*?depth\s+(\d+).*?status\s+(\w+)", 
            query_lower
        )
        
        if full_create_match:
            well_name = full_create_match.group(1).strip().upper()
            depth = full_create_match.group(2)
            status = full_create_match.group(3).upper()
            
            return {
                "intent": "write",
                "sql": f"INSERT INTO WELLS (WELL_NAME, STATUS, DEPTH) VALUES ('{well_name}', '{status}', {depth})"
            }
        
        # Pattern 0a: Create/Insert New Well (simple)
        # "create new well with name tariq" or "insert well named poseidon" or "add well X"
        create_match = re.search(r"(?:create|insert|add)(?:\s+new)?\s+well\s+(?:with\s+name\s+|named\s+)?(.+)", query_lower)
        
        if create_match:
            well_name = create_match.group(1).strip()
            # Remove common trailing words and check for commas
            well_name = re.sub(r'\s+(with|and|at).*$', '', well_name)
            
            # Skip if it contains commas (handled by full_create_match)
            if ',' in well_name:
                pass  # Let it fall through to other patterns
            else:
                well_name_upper = well_name.upper()
                
                return {
                    "intent": "write",
                    "sql": f"INSERT INTO WELLS (WELL_NAME, STATUS, DEPTH) VALUES ('{well_name_upper}', 'ACTIVE', 0)"
                }
        
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
                where_clause = f"WELL_NAME LIKE '%{well_identifier.upper()}%'"
                
            return {
                "intent": "write",
                "sql": f"UPDATE WELLS SET STATUS = '{new_status}' WHERE {where_clause}"
            }

        # Pattern 1c: Update Field Name
        # "update field name of well TARIQ to PORKISTAN"
        field_match = re.search(r"(?:change|update|set|edit|modify)\s+field\s+name\s+of\s+well\s+(.+?)\s+to\s+(.+)", query_lower)
        
        if field_match:
            well_identifier = field_match.group(1).strip()
            new_field = field_match.group(2).strip().upper()
            
            if well_identifier.isdigit():
                where_clause = f"WELL_ID = {well_identifier}"
            else:
                where_clause = f"WELL_NAME LIKE '%{well_identifier.upper()}%'"
                
            return {
                "intent": "write",
                "sql": f"UPDATE WELLS SET FIELD_NAME = '{new_field}' WHERE {where_clause}"
            }

        # Pattern 1c: Update Well Name
        # "update well a name to TARIQ" or "change well B name to NEWNAME" or "rename well C to CHARLIE"
        name_match = re.search(r"(?:update|change|set|edit|modify|rename)\s+well\s+(.+?)\s+(?:name\s+)?to\s+(.+)", query_lower)
        
        if name_match:
            well_identifier = name_match.group(1).strip()
            # Remove "name" if it appears in the identifier
            well_identifier = well_identifier.replace("name", "").strip()
            new_name = name_match.group(2).strip().upper()
            
            if well_identifier.isdigit():
                where_clause = f"WELL_ID = {well_identifier}"
            else:
                where_clause = f"WELL_NAME LIKE '%{well_identifier.upper()}%'"
                
            return {
                "intent": "write",
                "sql": f"UPDATE WELLS SET WELL_NAME = '{new_name}' WHERE {where_clause}"
            }

        # Pattern 1d: Partial Update (Missing Identifier)
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
