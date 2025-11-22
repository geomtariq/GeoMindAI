import pytest
from services.sql_validator import SQLSafetyValidator

@pytest.fixture
def validator():
    return SQLSafetyValidator()

def test_validate_read_only_allows_select(validator):
    assert validator.validate_read_only("SELECT * FROM wells") == True

def test_validate_read_only_denies_update(validator):
    assert validator.validate_read_only("UPDATE wells SET status = 'completed'") == False

def test_validate_write_allows_update(validator):
    assert validator.validate_write("UPDATE wells SET status = 'completed'") == True

def test_validate_write_denies_select(validator):
    assert validator.validate_write("SELECT * FROM wells") == False

def test_validate_write_allows_insert(validator):
    assert validator.validate_write("INSERT INTO wells (well_name) VALUES ('test')") == True
