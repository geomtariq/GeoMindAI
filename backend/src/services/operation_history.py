import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from copy import deepcopy
import uuid

logger = logging.getLogger(__name__)

class OperationHistory:
    """Manages operation history, snapshots, and undo/redo functionality."""
    
    def __init__(self, max_history=50):
        self.max_history = max_history
        # Session-based history: {session_id: {operations: [], undo_stack: [], redo_stack: []}}
        self.sessions = {}
    
    def _get_session(self, session_id: str) -> Dict:
        """Get or create session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "operations": [],
                "undo_stack": [],
                "redo_stack": []
            }
        return self.sessions[session_id]
    
    def capture_snapshot(self, session_id: str, sql: str, gateway) -> Dict[str, Any]:
        """
        Capture current data state before executing a write operation.
        Returns: {table: str, affected_rows: List[Dict], row_count: int}
        """
        try:
            # Determine which table will be affected
            sql_upper = sql.upper()
            table_name = None
            
            if "WELLS" in sql_upper:
                table_name = "WELLS"
                data = gateway.wells
            elif "PRODUCTION" in sql_upper:
                table_name = "PRODUCTION"
                data = gateway.production
            else:
                return {"table": "UNKNOWN", "affected_rows": [], "row_count": 0}
            
            # For UPDATE/DELETE, find affected rows
            if "UPDATE" in sql_upper or "DELETE" in sql_upper:
                # Parse WHERE conditions from SQL
                where_conditions = gateway._parse_where_clause(sql.lower())
                affected_rows = [
                    deepcopy(row) for row in data 
                    if gateway._matches_conditions(row, where_conditions)
                ]
            else:
                # For INSERT, no existing rows affected
                affected_rows = []
            
            return {
                "table": table_name,
                "affected_rows": affected_rows,
                "row_count": len(affected_rows)
            }
        except Exception as e:
            logger.error(f"Error capturing snapshot: {e}")
            return {"table": "UNKNOWN", "affected_rows": [], "row_count": 0}
    
    def generate_description(self, sql: str, before_snapshot: Dict, after_snapshot: Dict) -> str:
        """Generate plain English description of the operation."""
        sql_upper = sql.upper()
        
        try:
            if "INSERT" in sql_upper:
                # Extract well name from INSERT
                import re
                name_match = re.search(r"VALUES\s*\('([^']+)'", sql, re.IGNORECASE)
                well_name = name_match.group(1) if name_match else "new well"
                return f"Create a new well named '{well_name}'"
            
            elif "UPDATE" in sql_upper:
                # Extract what's being updated
                import re
                set_match = re.search(r"SET\s+(\w+)\s*=\s*(?:'([^']*)'|(\d+))", sql, re.IGNORECASE)
                where_match = re.search(r"WHERE\s+\w+\s+LIKE\s+'%([^%']+)%'", sql, re.IGNORECASE)
                
                if set_match and where_match:
                    field = set_match.group(1)
                    new_value = set_match.group(2) or set_match.group(3)
                    well_identifier = where_match.group(1)
                    
                    # Get old value from before snapshot
                    old_value = "unknown"
                    if before_snapshot["affected_rows"]:
                        old_value = before_snapshot["affected_rows"][0].get(field.upper(), "unknown")
                    
                    return f"Update {field} of well '{well_identifier}' from {old_value} to {new_value}"
                else:
                    return f"Update {before_snapshot['row_count']} row(s) in {before_snapshot['table']}"
            
            elif "DELETE" in sql_upper:
                import re
                where_match = re.search(r"WHERE\s+\w+\s+LIKE\s+'%([^%']+)%'", sql, re.IGNORECASE)
                well_identifier = where_match.group(1) if where_match else "matching rows"
                return f"Delete well '{well_identifier}'"
            
            else:
                return f"Execute: {sql[:50]}..."
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"Execute SQL operation"
    
    def record_operation(self, session_id: str, operation: Dict[str, Any]):
        """
        Record an operation in history.
        Operation format: {
            id, timestamp, sql, operation_type, description,
            before_snapshot, after_snapshot, affected_rows, can_undo
        }
        """
        session = self._get_session(session_id)
        
        # Add to operations list
        session["operations"].append(operation)
        
        # Add to undo stack
        session["undo_stack"].append(operation)
        
        # Clear redo stack (new operation invalidates redo)
        session["redo_stack"] = []
        
        # Trim history if too long
        if len(session["operations"]) > self.max_history:
            session["operations"] = session["operations"][-self.max_history:]
        if len(session["undo_stack"]) > self.max_history:
            session["undo_stack"] = session["undo_stack"][-self.max_history:]
        
        logger.info(f"Recorded operation {operation['id']} for session {session_id}")
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get operation history for a session."""
        session = self._get_session(session_id)
        operations = session["operations"][-limit:]
        return operations
    
    def generate_undo_sql(self, operation: Dict[str, Any]) -> str:
        """Generate SQL to undo an operation."""
        op_type = operation["operation_type"]
        before_snapshot = operation["before_snapshot"]
        sql = operation["sql"]
        
        if op_type == "INSERT":
            # Undo INSERT with DELETE
            import re
            name_match = re.search(r"VALUES\s*\('([^']+)'", sql, re.IGNORECASE)
            if name_match:
                well_name = name_match.group(1)
                return f"DELETE FROM WELLS WHERE WELL_NAME = '{well_name}'"
        
        elif op_type == "UPDATE":
            # Undo UPDATE by restoring old values
            if before_snapshot["affected_rows"]:
                old_row = before_snapshot["affected_rows"][0]
                # Extract what was updated
                import re
                set_match = re.search(r"SET\s+(\w+)\s*=", sql, re.IGNORECASE)
                where_match = re.search(r"WHERE\s+(.+)$", sql, re.IGNORECASE)
                
                if set_match and where_match:
                    field = set_match.group(1).upper()
                    where_clause = where_match.group(1)
                    old_value = old_row.get(field)
                    
                    if isinstance(old_value, str):
                        return f"UPDATE WELLS SET {field} = '{old_value}' WHERE {where_clause}"
                    else:
                        return f"UPDATE WELLS SET {field} = {old_value} WHERE {where_clause}"
        
        elif op_type == "DELETE":
            # Undo DELETE by re-inserting rows
            if before_snapshot["affected_rows"]:
                row = before_snapshot["affected_rows"][0]
                cols = ", ".join(row.keys())
                vals = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in row.values()])
                return f"INSERT INTO WELLS ({cols}) VALUES ({vals})"
        
        return None
    
    def undo_last(self, session_id: str, gateway) -> Optional[Dict]:
        """
        Undo the last operation.
        Returns: {status, undone_operation, undo_sql}
        """
        session = self._get_session(session_id)
        
        if not session["undo_stack"]:
            return None
        
        # Pop last operation
        operation = session["undo_stack"].pop()
        
        # Generate undo SQL
        undo_sql = self.generate_undo_sql(operation)
        
        if undo_sql:
            # Execute undo SQL
            try:
                gateway._execute_sql_internal(undo_sql)
                
                # Add to redo stack
                session["redo_stack"].append(operation)
                
                logger.info(f"Undid operation {operation['id']}")
                return {
                    "status": "success",
                    "undone_operation": operation,
                    "undo_sql": undo_sql
                }
            except Exception as e:
                logger.error(f"Error executing undo SQL: {e}")
                # Put operation back on undo stack
                session["undo_stack"].append(operation)
                return None
        
        return None
    
    def redo_last(self, session_id: str, gateway) -> Optional[Dict]:
        """
        Redo the last undone operation.
        Returns: {status, redone_operation, redo_sql}
        """
        session = self._get_session(session_id)
        
        if not session["redo_stack"]:
            return None
        
        # Pop last undone operation
        operation = session["redo_stack"].pop()
        
        # Re-execute original SQL
        try:
            gateway._execute_sql_internal(operation["sql"])
            
            # Add back to undo stack
            session["undo_stack"].append(operation)
            
            logger.info(f"Redid operation {operation['id']}")
            return {
                "status": "success",
                "redone_operation": operation,
                "redo_sql": operation["sql"]
            }
        except Exception as e:
            logger.error(f"Error executing redo SQL: {e}")
            # Put operation back on redo stack
            session["redo_stack"].append(operation)
            return None

# Create singleton instance
operation_history = OperationHistory()
