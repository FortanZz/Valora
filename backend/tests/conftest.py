import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def valid_user_data():
    """Fixture for valid user registration data"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def valid_property_data():
    """Fixture for valid property creation data"""
    return {
        "title": "Beautiful Test Apartment",
        "location": "Test Location",
        "price": 150000,
        "property_type": "apartment",
        "category": "sale",
        "contact_phone": "+389701234567",
        "contact_email": "test@example.com",
        "num_bedrooms": 2,
        "num_bathrooms": 1,
        "area_sqm": 85
    }
