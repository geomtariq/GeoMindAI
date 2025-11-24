import logging
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where
from sqlparse.tokens import Keyword, DML

logger = logging.getLogger(__name__)

class EnhancedSQLValidator:
    """
    Enhanced SQL validator with safety checks, complexity analysis, and injection prevention.
    """
    
    def __init__(self):
        self.dangerous_keywords = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        self.write_keywords = ['UPDATE', 'DELETE', 'INSERT']
        self.read_keywords = ['SELECT']
    
    def validate_read_only(self, sql: str) -> bool:
        """Validate that SQL is a read-only SELECT statement."""
        try:
            parsed = sqlparse.parse(sql)[0]
            first_token = parsed.token_first(skip_ws=True, skip_cm=True)
            
            if first_token and first_token.ttype is DML:
                return first_token.value.upper() == 'SELECT'
            return False
        except Exception as e:
            logger.error(f"Error validating read-only SQL: {e}")
            return False
    
    def validate_write(self, sql: str) -> bool:
        """Validate that SQL is a valid write statement."""
        try:
            parsed = sqlparse.parse(sql)[0]
            first_token = parsed.token_first(skip_ws=True, skip_cm=True)
            
            if first_token and first_token.ttype is DML:
                return first_token.value.upper() in self.write_keywords
            return False
        except Exception as e:
            logger.error(f"Error validating write SQL: {e}")
            return False
    
    def check_dangerous_operation(self, sql: str) -> dict:
        """
        Check if SQL contains dangerous operations.
        Returns: {"is_dangerous": bool, "reason": str, "requires_extra_confirmation": bool}
        """
        sql_upper = sql.upper()
        
        # Check for dangerous keywords
        for keyword in self.dangerous_keywords:
            if keyword in sql_upper:
                return {
                    "is_dangerous": True,
                    "reason": f"Contains {keyword} operation which can permanently modify database structure",
                    "requires_extra_confirmation": True
                }
        
        # Check for DELETE/UPDATE without WHERE clause
        if 'DELETE' in sql_upper or 'UPDATE' in sql_upper:
            if 'WHERE' not in sql_upper:
                return {
                    "is_dangerous": True,
                    "reason": "DELETE/UPDATE without WHERE clause will affect ALL rows",
                    "requires_extra_confirmation": True
                }
        
        return {"is_dangerous": False, "reason": "", "requires_extra_confirmation": False}
    
    def analyze_complexity(self, sql: str) -> dict:
        """
        Analyze query complexity.
        Returns: {"complexity": str, "warnings": list, "estimated_cost": str}
        """
        sql_upper = sql.upper()
        warnings = []
        complexity = "LOW"
        
        # Check for JOINs
        join_count = sql_upper.count('JOIN')
        if join_count > 0:
            complexity = "MEDIUM"
            if join_count > 3:
                complexity = "HIGH"
                warnings.append(f"Query contains {join_count} JOINs which may be slow")
        
        # Check for subqueries
        subquery_count = sql_upper.count('SELECT') - 1  # Subtract main SELECT
        if subquery_count > 0:
            complexity = "MEDIUM" if complexity == "LOW" else "HIGH"
            warnings.append(f"Query contains {subquery_count} subqueries")
        
        # Check for aggregations
        if any(agg in sql_upper for agg in ['GROUP BY', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX']):
            if complexity == "LOW":
                complexity = "MEDIUM"
        
        # Estimate cost
        estimated_cost = {
            "LOW": "< 100ms",
            "MEDIUM": "100ms - 1s",
            "HIGH": "> 1s"
        }.get(complexity, "Unknown")
        
        return {
            "complexity": complexity,
            "warnings": warnings,
            "estimated_cost": estimated_cost
        }
    
    def check_sql_injection(self, sql: str) -> dict:
        """
        Check for potential SQL injection patterns.
        Returns: {"is_safe": bool, "issues": list}
        """
        issues = []
        
        # Check for common injection patterns
        dangerous_patterns = [
            ("--", "SQL comment detected"),
            (";", "Multiple statements detected"),
            ("UNION", "UNION statement detected"),
            ("EXEC", "EXEC command detected"),
            ("EXECUTE", "EXECUTE command detected")
        ]
        
        sql_upper = sql.upper()
        for pattern, message in dangerous_patterns:
            if pattern in sql_upper:
                # Allow semicolon at end
                if pattern == ";" and sql.strip().endswith(";"):
                    continue
                issues.append(message)
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues
        }
    
    def validate_comprehensive(self, sql: str, intent: str) -> dict:
        """
        Comprehensive validation combining all checks.
        Returns: {"is_valid": bool, "errors": list, "warnings": list, "metadata": dict}
        """
        errors = []
        warnings = []
        metadata = {}
        
        # Basic validation
        if intent == 'read':
            if not self.validate_read_only(sql):
                errors.append("SQL is not a valid read-only query")
        elif intent == 'write':
            if not self.validate_write(sql):
                errors.append("SQL is not a valid write query")
        
        # Danger check
        danger_check = self.check_dangerous_operation(sql)
        if danger_check["is_dangerous"]:
            warnings.append(danger_check["reason"])
            metadata["requires_extra_confirmation"] = True
        
        # Complexity analysis
        complexity = self.analyze_complexity(sql)
        metadata["complexity"] = complexity["complexity"]
        metadata["estimated_cost"] = complexity["estimated_cost"]
        warnings.extend(complexity["warnings"])
        
        # Injection check
        injection_check = self.check_sql_injection(sql)
        if not injection_check["is_safe"]:
            errors.extend([f"Security issue: {issue}" for issue in injection_check["issues"]])
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }

# Create singleton instance
sql_validator = EnhancedSQLValidator()
