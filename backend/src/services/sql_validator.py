# This file will contain the logic for the SQL Safety Validator.
# It will be responsible for ensuring that AI-generated SQL is safe to execute.

class SQLSafetyValidator:
    def __init__(self):
        # TODO: Add more sophisticated rules, such as checking for denied tables,
        # complex joins, or functions that could be harmful.
        self.allowed_statement_types = ["SELECT"]

    def validate_read_only(self, sql: str) -> bool:
        """
        Validates that the SQL statement is a read-only query.
        """
        statement_type = sql.strip().upper().split()[0]
        return statement_type in self.allowed_statement_types

sql_validator = SQLSafetyValidator()
