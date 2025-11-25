import logging
import re
from typing import List, Dict, Any
from copy import deepcopy

logger = logging.getLogger(__name__)

class EnhancedMockOracleGateway:
    """Enhanced mock Oracle gateway with support for JOIN, aggregates, complex queries, and DDL."""
    
    def __init__(self):
        self._pools = {}
        
        # Dynamic storage for tables created at runtime
        # Structure: {"TABLE_NAME": {"columns": [{"name": "COL", "type": "TYPE"}], "data": []}}
        self.dynamic_tables = {}
        
        # Initialize comprehensive test data (Hardcoded for initial state)
        self.wells = [
            {"WELL_ID": 1, "WELL_NAME": "MOCK WELL A", "DEPTH": 1000, "STATUS": "ACTIVE", "FIELD_NAME": "POSEIDON", "OPERATOR": "ACME OIL"},
            {"WELL_ID": 2, "WELL_NAME": "MOCK WELL B", "DEPTH": 2500, "STATUS": "INACTIVE", "FIELD_NAME": "POSEIDON", "OPERATOR": "ACME OIL"},
            {"WELL_ID": 3, "WELL_NAME": "MOCK WELL C", "DEPTH": 1500, "STATUS": "ACTIVE", "FIELD_NAME": "NEPTUNE", "OPERATOR": "BETA ENERGY"},
        ]
        
        self.production = [
            {"PRODUCTION_ID": 1, "WELL_ID": 1, "PRODUCTION_DATE": "2024-01-01", "OIL_VOLUME": 500, "GAS_VOLUME": 1000, "WATER_VOLUME": 100},
            {"PRODUCTION_ID": 2, "WELL_ID": 1, "PRODUCTION_DATE": "2024-01-02", "OIL_VOLUME": 520, "GAS_VOLUME": 1050, "WATER_VOLUME": 105},
            {"PRODUCTION_ID": 3, "WELL_ID": 2, "PRODUCTION_DATE": "2024-01-01", "OIL_VOLUME": 800, "GAS_VOLUME": 1500, "WATER_VOLUME": 150},
            {"PRODUCTION_ID": 4, "WELL_ID": 3, "PRODUCTION_DATE": "2024-01-01", "OIL_VOLUME": 600, "GAS_VOLUME": 1200, "WATER_VOLUME": 120},
        ]
        
        self.seismic_surveys = [
            {"SURVEY_ID": 1, "SURVEY_NAME": "POSEIDON 3D", "SURVEY_TYPE": "3D", "ACQUISITION_DATE": "2023-06-15", "AREA": 250, "CONTRACTOR": "SEISMIC INC"},
            {"SURVEY_ID": 2, "SURVEY_NAME": "NEPTUNE 2D", "SURVEY_TYPE": "2D", "ACQUISITION_DATE": "2023-08-20", "AREA": 150, "CONTRACTOR": "GEO SERVICES"},
        ]
        
        self.well_logs = [
            {"LOG_ID": 1, "WELL_ID": 1, "LOG_TYPE": "GR", "LOG_DATE": "2024-01-15", "TOP_DEPTH": 0, "BOTTOM_DEPTH": 1000},
            {"LOG_ID": 2, "WELL_ID": 1, "LOG_TYPE": "RESISTIVITY", "LOG_DATE": "2024-01-15", "TOP_DEPTH": 0, "BOTTOM_DEPTH": 1000},
            {"LOG_ID": 3, "WELL_ID": 2, "LOG_TYPE": "GR", "LOG_DATE": "2024-01-20", "TOP_DEPTH": 0, "BOTTOM_DEPTH": 2500},
        ]
        
        self.markers = [
            {"MARKER_ID": 1, "WELL_ID": 1, "MARKER_NAME": "TOP RESERVOIR", "DEPTH": 800, "FORMATION": "SANDSTONE A", "INTERPRETER": "JOHN DOE"},
            {"MARKER_ID": 2, "WELL_ID": 1, "MARKER_NAME": "BASE RESERVOIR", "DEPTH": 950, "FORMATION": "SANDSTONE A", "INTERPRETER": "JOHN DOE"},
            {"MARKER_ID": 3, "WELL_ID": 2, "MARKER_NAME": "TOP RESERVOIR", "DEPTH": 2000, "FORMATION": "SANDSTONE B", "INTERPRETER": "JANE SMITH"},
        ]

    def create_pool_for_session(self, session_id: str, db_config: dict):
        """Mocks creating a connection pool."""
        logger.info(f"[MOCK] Creating pool for session {session_id}")
        self._pools[session_id] = "mock_pool"

    def get_schema_metadata(self) -> Dict[str, Any]:
        """
        Simulate retrieving database schema metadata.
        Returns a dictionary structure representing tables and columns.
        """
        logger.info("[MOCK] Retrieving schema metadata")
        
        # Base hardcoded tables
        tables = [
            {
                "name": "WELLS",
                "columns": [
                    {"name": "WELL_ID", "type": "NUMBER", "pk": True},
                    {"name": "WELL_NAME", "type": "VARCHAR2(100)", "constraints": "UNIQUE, NOT NULL"},
                    {"name": "DEPTH", "type": "NUMBER", "constraints": "DEFAULT 0"},
                    {"name": "STATUS", "type": "VARCHAR2(20)"},
                    {"name": "LATITUDE", "type": "NUMBER"},
                    {"name": "LONGITUDE", "type": "NUMBER"},
                    {"name": "SPUD_DATE", "type": "DATE"},
                    {"name": "COMPLETION_DATE", "type": "DATE"},
                    {"name": "FIELD_NAME", "type": "VARCHAR2(100)"},
                    {"name": "OPERATOR", "type": "VARCHAR2(100)"}
                ]
            },
            {
                "name": "PRODUCTION",
                "columns": [
                    {"name": "PRODUCTION_ID", "type": "NUMBER", "pk": True},
                    {"name": "WELL_ID", "type": "NUMBER", "fk": "WELLS.WELL_ID"},
                    {"name": "PRODUCTION_DATE", "type": "DATE"},
                    {"name": "OIL_VOLUME", "type": "NUMBER"},
                    {"name": "GAS_VOLUME", "type": "NUMBER"},
                    {"name": "WATER_VOLUME", "type": "NUMBER"}
                ]
            },
            {
                "name": "SEISMIC_SURVEYS",
                "columns": [
                    {"name": "SURVEY_ID", "type": "NUMBER", "pk": True},
                    {"name": "SURVEY_NAME", "type": "VARCHAR2(100)"},
                    {"name": "SURVEY_TYPE", "type": "VARCHAR2(50)"},
                    {"name": "ACQUISITION_DATE", "type": "DATE"},
                    {"name": "AREA", "type": "NUMBER"},
                    {"name": "CONTRACTOR", "type": "VARCHAR2(100)"}
                ]
            },
            {
                "name": "WELL_LOGS",
                "columns": [
                    {"name": "LOG_ID", "type": "NUMBER", "pk": True},
                    {"name": "WELL_ID", "type": "NUMBER", "fk": "WELLS.WELL_ID"},
                    {"name": "LOG_TYPE", "type": "VARCHAR2(50)"},
                    {"name": "LOG_DATE", "type": "DATE"},
                    {"name": "TOP_DEPTH", "type": "NUMBER"},
                    {"name": "BOTTOM_DEPTH", "type": "NUMBER"}
                ]
            },
            {
                "name": "MARKERS",
                "columns": [
                    {"name": "MARKER_ID", "type": "NUMBER", "pk": True},
                    {"name": "WELL_ID", "type": "NUMBER", "fk": "WELLS.WELL_ID"},
                    {"name": "MARKER_NAME", "type": "VARCHAR2(100)"},
                    {"name": "DEPTH", "type": "NUMBER"},
                    {"name": "FORMATION", "type": "VARCHAR2(100)"},
                    {"name": "INTERPRETER", "type": "VARCHAR2(100)"}
                ]
            }
        ]
        
        # Add dynamic tables
        for table_name, table_info in self.dynamic_tables.items():
            tables.append({
                "name": table_name,
                "columns": table_info["columns"]
            })
            
        return {"tables": tables}

    def get_table_data(self, table_name: str) -> List[Dict]:
        """Get data for a specific table."""
        table_name_upper = table_name.upper()
        
        # Check dynamic tables first
        if table_name_upper in self.dynamic_tables:
            return self.dynamic_tables[table_name_upper]["data"]
            
        table_map = {
            "WELLS": self.wells,
            "PRODUCTION": self.production,
            "SEISMIC_SURVEYS": self.seismic_surveys,
            "WELL_LOGS": self.well_logs,
            "MARKERS": self.markers
        }
        return table_map.get(table_name_upper, [])

    def simulate_query(self, sql: str) -> List[Dict]:
        """Simulate query execution without persisting changes (for preview)."""
        # Create a deep copy of data
        original_wells = deepcopy(self.wells)
        original_production = deepcopy(self.production)
        original_dynamic = deepcopy(self.dynamic_tables)
        
        try:
            # Execute query
            result = self.execute_query_internal_logic(sql)
            return result
        finally:
            # Restore original data
            self.wells = original_wells
            self.production = original_production
            self.dynamic_tables = original_dynamic

    def execute_query(self, session_id: str, sql: str) -> List[Dict]:
        """Execute query and persist changes."""
        logger.info(f"[MOCK] Executing query for session {session_id}: {sql}")
        
        if session_id not in self._pools:
            raise ValueError("No database connection for this session.")
        
        return self.execute_query_internal_logic(sql)

    def execute_query_internal_logic(self, sql: str) -> List[Dict]:
        """
        Handles execution of one or more SQL statements separated by semicolons.
        Returns the result of the LAST statement (or combined results if needed, but usually last for display).
        """
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        last_result = []
        
        for stmt in statements:
            last_result = self._execute_single_statement(stmt)
            
        return last_result

    def _execute_single_statement(self, sql: str) -> List[Dict]:
        """Internal method to execute a single SQL statement."""
        # Handle Error Messages returned as SQL
        if sql.startswith("SELECT '") and ("FROM DUAL" in sql.upper() or "Error" in sql):
            msg = sql.split("'")[1]
            return [{"MESSAGE": msg}]

        lower_sql = sql.lower()

        # Handle CREATE TABLE
        if "create table" in lower_sql:
            return self._handle_create_table(sql, lower_sql)

        # Handle UPDATE
        if "update" in lower_sql:
            return self._handle_update(sql, lower_sql)
        
        # Handle DELETE
        if "delete" in lower_sql:
            return self._handle_delete(sql, lower_sql)
        
        # Handle INSERT
        if "insert" in lower_sql:
            return self._handle_insert(sql, lower_sql)
        
        # Handle SELECT
        if "select" in lower_sql:
            return self._handle_select(sql, lower_sql)
        
        return []

    def _handle_create_table(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle CREATE TABLE operations."""
        # Parse table name
        match = re.search(r"create\s+table\s+(\w+)\s*\((.+)\)", sql, re.IGNORECASE | re.DOTALL)
        if match:
            table_name = match.group(1).upper()
            columns_def = match.group(2)
            
            columns = []
            # Simple column parser (splits by comma, assumes name type ...)
            # This is a mock, so it won't handle complex nested parens perfectly
            for col_def in columns_def.split(','):
                parts = col_def.strip().split()
                if len(parts) >= 2:
                    col_name = parts[0].upper()
                    col_type = ' '.join(parts[1:])
                    columns.append({"name": col_name, "type": col_type})
            
            self.dynamic_tables[table_name] = {
                "columns": columns,
                "data": []
            }
            logger.info(f"[MOCK] Created table {table_name}")
            return [{"MESSAGE": f"Table {table_name} created successfully."}]
            
        return [{"MESSAGE": "Failed to parse CREATE TABLE statement."}]

    def _handle_update(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle UPDATE operations."""
        # Identify table
        table_match = re.search(r"update\s+(\w+)", lower_sql)
        if not table_match:
            return []
        table_name = table_match.group(1).upper()
        
        data = self.get_table_data(table_name)
        if not data and table_name not in self.dynamic_tables: # Allow updating empty dynamic tables (though no rows to update)
             if table_name not in ["WELLS", "PRODUCTION", "SEISMIC_SURVEYS", "WELL_LOGS", "MARKERS"]:
                 return [{"MESSAGE": f"Table {table_name} not found."}]

        # Use original SQL for SET clause to preserve case
        set_match = re.search(r"set\s+(.+?)(?:\s+where|$)", sql, re.IGNORECASE)
        if not set_match:
            return []
        
        set_clause = set_match.group(1)
        
        # Parse SET assignments
        updates = {}
        for match in re.finditer(r"(\w+)\s*=\s*(?:'([^']*)'|(\d+))", set_clause):
            col_name = match.group(1).upper()
            value = match.group(2) if match.group(2) is not None else int(match.group(3))
            updates[col_name] = value
        
        # Parse WHERE clause
        where_conditions = self._parse_where_clause(lower_sql)
        
        # Apply updates
        updated_count = 0
        for row in data:
            if self._matches_conditions(row, where_conditions):
                for col, val in updates.items():
                    # In dynamic tables, we might need to add columns if they don't exist in the row yet?
                    # Or assume schema is strict. For mock, let's be flexible.
                    row[col] = val
                updated_count += 1
        
        logger.info(f"[MOCK] Updated {updated_count} rows in {table_name}")
        return []

    def _handle_delete(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle DELETE operations."""
        # Identify table
        table_match = re.search(r"delete\s+from\s+(\w+)", lower_sql)
        if not table_match:
            return []
        table_name = table_match.group(1).upper()
        
        data = self.get_table_data(table_name)
        
        where_conditions = self._parse_where_clause(lower_sql)
        
        initial_count = len(data)
        new_data = [row for row in data if not self._matches_conditions(row, where_conditions)]
        
        # Update the data source
        if table_name in self.dynamic_tables:
            self.dynamic_tables[table_name]["data"] = new_data
        elif table_name == "WELLS":
            self.wells = new_data
        elif table_name == "PRODUCTION":
            self.production = new_data
        # ... (other hardcoded tables)
        
        deleted_count = initial_count - len(new_data)
        
        logger.info(f"[MOCK] Deleted {deleted_count} rows from {table_name}")
        return []

    def _handle_insert(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle INSERT operations."""
        # Identify table
        table_match = re.search(r"insert\s+into\s+(\w+)", lower_sql)
        if not table_match:
            return []
        table_name = table_match.group(1).upper()
        
        # Use original SQL for VALUES to preserve case
        cols_match = re.search(r"\(([^)]+)\)\s*values", sql, re.IGNORECASE)
        vals_match = re.search(r"values\s*\(([^)]+)\)", sql, re.IGNORECASE)
        
        if cols_match and vals_match:
            cols = [c.strip().upper() for c in cols_match.group(1).split(',')]
            vals_str = vals_match.group(1)
            
            # Parse values
            vals = []
            for match in re.finditer(r"'([^']*)'|(\d+)", vals_str):
                vals.append(match.group(1) if match.group(1) is not None else int(match.group(2)))
            
            # Create new record
            new_record = {}
            for col, val in zip(cols, vals):
                new_record[col] = val
            
            # Auto-generate ID if needed (simple heuristic)
            id_col = f"{table_name[:-1]}_ID" if table_name.endswith('S') else f"{table_name}_ID"
            if id_col not in new_record:
                data = self.get_table_data(table_name)
                current_max = max([row.get(id_col, 0) for row in data], default=0) if data else 0
                new_record[id_col] = current_max + 1
            
            # Append to correct table
            if table_name in self.dynamic_tables:
                self.dynamic_tables[table_name]["data"].append(new_record)
            elif table_name == "WELLS":
                self.wells.append(new_record)
            elif table_name == "PRODUCTION":
                self.production.append(new_record)
            # ... others
            
            logger.info(f"[MOCK] Inserted into {table_name}: {new_record}")
        
        return []

    def _handle_select(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle SELECT operations including JOINs and aggregates."""
        
        # Handle COUNT queries
        if "count(*)" in lower_sql or "count(1)" in lower_sql:
            return self._handle_count(sql, lower_sql)
        
        # Handle aggregate functions (AVG, SUM, MIN, MAX)
        if any(agg in lower_sql for agg in ["avg(", "sum(", "min(", "max("]):
            return self._handle_aggregate(sql, lower_sql)
        
        # Handle JOIN queries
        if "join" in lower_sql:
            return self._handle_join(sql, lower_sql)
        
        # Handle simple SELECT
        return self._handle_simple_select(sql, lower_sql)

    def _handle_count(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle COUNT queries."""
        # Determine table
        match = re.search(r"from\s+(\w+)", lower_sql)
        if not match:
             return [{"COUNT(*)": 0}]
        
        table_name = match.group(1).upper()
        data = self.get_table_data(table_name)
        
        # Apply WHERE conditions
        where_conditions = self._parse_where_clause(lower_sql)
        if where_conditions:
            data = [row for row in data if self._matches_conditions(row, where_conditions)]
        
        return [{"COUNT(*)": len(data)}]

    def _handle_aggregate(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle aggregate functions with GROUP BY."""
        # Extract aggregate function and column
        agg_match = re.search(r"(avg|sum|min|max)\((\w+)\)", lower_sql)
        if not agg_match:
            return []
        
        agg_func = agg_match.group(1).upper()
        agg_col = agg_match.group(2).upper()
        
        # Determine table
        match = re.search(r"from\s+(\w+)", lower_sql)
        if not match:
             return []
        table_name = match.group(1).upper()
        data = self.get_table_data(table_name)
        
        # Check for GROUP BY
        group_by_match = re.search(r"group\s+by\s+(\w+)", lower_sql)
        
        if group_by_match:
            # Group by column
            group_col = group_by_match.group(1).upper()
            groups = {}
            
            for row in data:
                key = row.get(group_col, "NULL")
                if key not in groups:
                    groups[key] = []
                groups[key].append(row.get(agg_col, 0))
            
            # Calculate aggregates
            results = []
            for key, values in groups.items():
                if agg_func == "AVG":
                    result_val = sum(values) / len(values) if values else 0
                elif agg_func == "SUM":
                    result_val = sum(values)
                elif agg_func == "MIN":
                    result_val = min(values) if values else 0
                elif agg_func == "MAX":
                    result_val = max(values) if values else 0
                else:
                    result_val = 0
                
                results.append({group_col: key, f"{agg_func}({agg_col})": result_val})
            
            return results
        else:
            # No GROUP BY, single aggregate
            values = [row.get(agg_col, 0) for row in data]
            if agg_func == "AVG":
                result_val = sum(values) / len(values) if values else 0
            elif agg_func == "SUM":
                result_val = sum(values)
            elif agg_func == "MIN":
                result_val = min(values) if values else 0
            elif agg_func == "MAX":
                result_val = max(values) if values else 0
            else:
                result_val = 0
            
            return [{f"{agg_func}({agg_col})": result_val}]

    def _handle_join(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle JOIN queries."""
        # Simple JOIN implementation for PRODUCTION JOIN WELLS
        if "production" in lower_sql and "wells" in lower_sql:
            results = []
            for prod in self.production:
                for well in self.wells:
                    if prod["WELL_ID"] == well["WELL_ID"]:
                        # Merge records
                        merged = {**prod, **well}
                        # Apply WHERE conditions
                        where_conditions = self._parse_where_clause(lower_sql)
                        if not where_conditions or self._matches_conditions(merged, where_conditions):
                            results.append(merged)
            return results
        
        return []

    def _handle_simple_select(self, sql: str, lower_sql: str) -> List[Dict]:
        """Handle simple SELECT queries."""
        # Determine table
        match = re.search(r"from\s+(\w+)", lower_sql)
        if not match:
             return [{"MOCK_COL_1": "Value 1", "MOCK_COL_2": "Value 2"}]
        
        table_name = match.group(1).upper()
        data = self.get_table_data(table_name)
        
        # Apply WHERE conditions
        where_conditions = self._parse_where_clause(lower_sql)
        if where_conditions:
            data = [row for row in data if self._matches_conditions(row, where_conditions)]
        
        return data

    def _parse_where_clause(self, lower_sql: str) -> List[Dict]:
        """Parse WHERE clause into conditions."""
        conditions = []
        
        # Extract WHERE clause
        where_match = re.search(r"where\s+(.+?)(?:\s+group\s+by|\s+order\s+by|$)", lower_sql)
        if not where_match:
            return conditions
        
        where_clause = where_match.group(1)
        
        # Parse conditions (simple implementation)
        # Handle LIKE
        like_matches = re.finditer(r"(\w+)\s+like\s+'%?([^'%]+)%?'", where_clause)
        for match in like_matches:
            conditions.append({
                "column": match.group(1).upper(),
                "operator": "LIKE",
                "value": match.group(2).upper()
            })
        
        # Handle = (equality)
        # Support UPPER(col) or LOWER(col)
        eq_matches = re.finditer(r"(?:UPPER\(|LOWER\()?\s*(\w+)\s*(?:\))?\s*=\s*(?:'([^']*)'|(\d+))", where_clause, re.IGNORECASE)
        for match in eq_matches:
            if "like" not in where_clause[max(0, match.start()-10):match.start()].lower():
                conditions.append({
                    "column": match.group(1).upper(),
                    "operator": "=",
                    "value": match.group(2).upper() if match.group(2) else int(match.group(3))
                })
        
        # Handle > (greater than)
        gt_matches = re.finditer(r"(\w+)\s*>\s*(\d+)", where_clause)
        for match in gt_matches:
            conditions.append({
                "column": match.group(1).upper(),
                "operator": ">",
                "value": int(match.group(2))
            })
        
        return conditions

    def _matches_conditions(self, row: Dict, conditions: List[Dict]) -> bool:
        """Check if a row matches all WHERE conditions."""
        if not conditions:
            return True
        
        for cond in conditions:
            col = cond["column"]
            op = cond["operator"]
            val = cond["value"]
            
            if col not in row:
                return False
            
            row_val = row[col]
            
            if op == "LIKE":
                if isinstance(row_val, str) and val not in row_val.upper():
                    return False
            elif op == "=":
                # Special handling for WELL_NAME: allow partial match if exact match fails
                # This makes the mock DB more robust if AI generates '=' instead of 'LIKE'
                if col == "WELL_NAME" and isinstance(row_val, str) and isinstance(val, str):
                    if row_val != val and val not in row_val.upper():
                        return False
                elif row_val != val:
                    return False
            elif op == ">":
                if not (isinstance(row_val, (int, float)) and row_val > val):
                    return False
        
        return True

# Create singleton instance
mock_oracle_gateway = EnhancedMockOracleGateway()
