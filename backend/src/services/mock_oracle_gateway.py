import logging
import re

logger = logging.getLogger(__name__)

class MockOracleGateway:
    def __init__(self):
        self._pools = {}
        # Initialize stateful data
        self.wells = [
            {"WELL_ID": 1, "WELL_NAME": "MOCK WELL A", "DEPTH": 1000, "STATUS": "ACTIVE"},
            {"WELL_ID": 2, "WELL_NAME": "MOCK WELL B", "DEPTH": 2500, "STATUS": "INACTIVE"},
            {"WELL_ID": 3, "WELL_NAME": "MOCK WELL C", "DEPTH": 1500, "STATUS": "ACTIVE"},
        ]

    def create_pool_for_session(self, session_id: str, db_config: dict):
        """Mocks creating a connection pool."""
        logger.info(f"[MOCK] Creating pool for session {session_id} with config {db_config}")
        self._pools[session_id] = "mock_pool"

    def execute_query(self, session_id: str, sql: str) -> list[dict]:
        """Mocks executing a query."""
        logger.info(f"[MOCK] Executing query for session {session_id}: {sql}")
        
        if session_id not in self._pools:
             raise ValueError("No database connection for this session.")

        # Handle Error Messages returned as SQL
        if sql.startswith("SELECT '") and (sql.endswith("' FROM DUAL") or "Error" in sql):
             msg = sql.split("'")[1]
             return [{"MESSAGE": msg}]

        lower_sql = sql.lower()

        # Handle UPDATE
        if "update" in lower_sql:
            # General UPDATE parser: UPDATE table SET col1=val1, col2=val2 WHERE ...
            # Extract all SET clauses
            set_match = re.search(r"set\s+(.+?)\s+where", lower_sql)
            if not set_match:
                # No WHERE clause, update all (dangerous but we'll allow it)
                set_match = re.search(r"set\s+(.+)$", lower_sql)
            
            if set_match:
                set_clause = set_match.group(1)
                
                # Parse WHERE clause
                id_match = re.search(r"where\s+well_id\s*=\s*(\d+)", lower_sql)
                name_match = re.search(r"where\s+well_name\s*=\s*'(.+?)'", lower_sql)
                
                # Parse SET assignments (col = val, col2 = val2)
                updates = {}
                # Match patterns like: DEPTH = 1000, STATUS = 'ACTIVE', WELL_NAME = 'Tariq'
                for match in re.finditer(r"(\w+)\s*=\s*(?:'([^']*)'|(\d+))", set_clause):
                    col_name = match.group(1).upper()
                    # Value is either in group 2 (string) or group 3 (number)
                    value = match.group(2) if match.group(2) is not None else int(match.group(3))
                    updates[col_name] = value
                
                updated_count = 0
                for well in self.wells:
                    should_update = False
                    if id_match and well["WELL_ID"] == int(id_match.group(1)):
                        should_update = True
                    elif name_match and name_match.group(1).upper() in well["WELL_NAME"]:
                        should_update = True
                    elif not id_match and not name_match:
                        # No WHERE clause, update all
                        should_update = True
                    
                    if should_update:
                        for col, val in updates.items():
                            if col in well:
                                well[col] = val
                        updated_count += 1
                
                if updated_count > 0:
                    logger.info(f"[MOCK] Updated {updated_count} wells with {updates}")
                    return []
                else:
                    logger.warning("[MOCK] No wells matched for update.")
                    return []

        # Handle DELETE
        if "delete" in lower_sql:
            id_match = re.search(r"where\s+well_id\s*=\s*(\d+)", lower_sql)
            name_match = re.search(r"where\s+well_name\s*=\s*'(.+?)'", lower_sql)
            
            initial_count = len(self.wells)
            if id_match:
                target_id = int(id_match.group(1))
                self.wells = [w for w in self.wells if w["WELL_ID"] != target_id]
            elif name_match:
                target_name = name_match.group(1).upper()
                self.wells = [w for w in self.wells if target_name not in w["WELL_NAME"]]
            
            deleted_count = initial_count - len(self.wells)
            if deleted_count > 0:
                logger.info(f"[MOCK] Deleted {deleted_count} wells.")
            else:
                logger.warning("[MOCK] No wells matched for deletion.")
            return []

        # Handle INSERT
        if "insert" in lower_sql:
            # Parse INSERT INTO WELLS (col1, col2, ...) VALUES (val1, val2, ...)
            cols_match = re.search(r"insert\s+into\s+wells\s*\(([^)]+)\)", lower_sql)
            vals_match = re.search(r"values\s*\(([^)]+)\)", lower_sql)
            
            if cols_match and vals_match:
                cols = [c.strip().upper() for c in cols_match.group(1).split(',')]
                vals_str = vals_match.group(1)
                
                # Parse values (handle both strings and numbers)
                vals = []
                for match in re.finditer(r"'([^']*)'|(\d+)", vals_str):
                    vals.append(match.group(1) if match.group(1) is not None else int(match.group(2)))
                
                # Create new well record
                new_well = {}
                for col, val in zip(cols, vals):
                    new_well[col] = val
                
                # Auto-generate WELL_ID if not provided
                if "WELL_ID" not in new_well:
                    new_well["WELL_ID"] = max([w["WELL_ID"] for w in self.wells], default=0) + 1
                
                self.wells.append(new_well)
                logger.info(f"[MOCK] Inserted new well: {new_well}")
                return []

        # Handle SELECT
        if "select" in lower_sql:
            if "count" in lower_sql and "wells" in lower_sql:
                 return [{"COUNT(*)": len(self.wells)}]
            
            if "wells" in lower_sql:
                # Check for WHERE clause
                id_match = re.search(r"where\s+well_id\s*=\s*(\d+)", lower_sql)
                name_match = re.search(r"where\s+well_name\s*=\s*'(.+?)'", lower_sql)
                
                filtered_wells = self.wells
                if id_match:
                    target_id = int(id_match.group(1))
                    filtered_wells = [w for w in self.wells if w["WELL_ID"] == target_id]
                elif name_match:
                    target_name = name_match.group(1).upper()
                    # Use 'in' for partial matching here too
                    filtered_wells = [w for w in self.wells if target_name in w["WELL_NAME"]]
                
                return filtered_wells

            elif "production" in lower_sql:
                 return [
                    {"WELL_ID": 1, "DATE": "2023-01-01", "VOLUME": 500},
                    {"WELL_ID": 1, "DATE": "2023-01-02", "VOLUME": 520},
                ]
            else:
                return [{"MOCK_COL_1": "Value 1", "MOCK_COL_2": "Value 2"}]
        
        return []

mock_oracle_gateway = MockOracleGateway()
