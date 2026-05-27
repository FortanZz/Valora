import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.schemas.property import PropertyCreate, PropertyType, PropertyCategory


class TestUserSchemas:
    """Tests for user validation schemas"""

    def test_user_register_valid(self):
        """Test valid user registration data"""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        }
        user = UserRegister(**user_data)
        assert user.email == "user@example.com"
        assert user.first_name == "John"

    def test_user_register_weak_password(self):
        """Test registration with weak password"""
        user_data = {
            "email": "user@example.com",
            "password": "weak",
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        assert "Password" in str(exc_info.value)

    def test_user_register_password_no_uppercase(self):
        """Test password without uppercase letter"""
        user_data = {
            "email": "user@example.com",
            "password": "securepas123",
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegister(**user_data)

    def test_user_register_password_no_digit(self):
        """Test password without digit"""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePass",
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegister(**user_data)

    def test_user_register_invalid_email(self):
        """Test invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegister(**user_data)

    def test_user_login_valid(self):
        """Test valid user login data"""
        login_data = {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        user_login = UserLogin(**login_data)
        assert user_login.email == "user@example.com"


class TestPropertySchemas:
    """Tests for property validation schemas"""

    def test_property_create_valid(self):
        """Test valid property creation"""
        property_data = {
            "title": "Beautiful Apartment",
            "location": "Downtown Skopje",
            "price": 150000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com",
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "area_sqm": 85
        }
        prop = PropertyCreate(**property_data)
        assert prop.title == "Beautiful Apartment"
        assert prop.price == 150000

    def test_property_create_land_cannot_be_rented(self):
        """Test that land cannot be rented (business rule)"""
        property_data = {
            "title": "Land Plot",
            "location": "Suburban Area",
            "price": 50000,
            "property_type": "land",
            "category": "rent",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        with pytest.raises(ValidationError) as exc_info:
            PropertyCreate(**property_data)
        assert "cannot be rented" in str(exc_info.value).lower()

    def test_property_create_land_for_sale_valid(self):
        """Test that land can be sold"""
        property_data = {
            "title": "Land Plot",
            "location": "Suburban Area",
            "price": 50000,
            "property_type": "land",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        prop = PropertyCreate(**property_data)
        assert prop.property_type == PropertyType.LAND
        assert prop.category == PropertyCategory.SALE

    def test_property_create_invalid_price(self):
        """Test invalid price values"""
        property_data = {
            "title": "Apartment",
            "location": "Downtown",
            "price": -1000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        with pytest.raises(ValidationError):
            PropertyCreate(**property_data)

    def test_property_create_price_too_high(self):
        """Test price exceeding maximum"""
        property_data = {
            "title": "Apartment",
            "location": "Downtown",
            "price": 100_000_000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        with pytest.raises(ValidationError):
            PropertyCreate(**property_data)

    def test_property_create_price_too_low(self):
        """Test price below minimum"""
        property_data = {
            "title": "Apartment",
            "location": "Downtown",
            "price": 50,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        with pytest.raises(ValidationError):
            PropertyCreate(**property_data)

    def test_property_create_title_too_short(self):
        """Test title below minimum length"""
        property_data = {
            "title": "Apt",
            "location": "Downtown",
            "price": 150000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "seller@example.com"
        }
        with pytest.raises(ValidationError):
            PropertyCreate(**property_data)

    def test_property_create_all_types(self):
        """Test property creation with all property types"""
        for prop_type in [PropertyType.HOUSE, PropertyType.APARTMENT, PropertyType.OFFICE]:
            property_data = {
                "title": f"Beautiful {prop_type.value}",
                "location": "Downtown Skopje",
                "price": 150000,
                "property_type": prop_type.value,
                "category": "sale",
                "contact_phone": "+389701234567",
                "contact_email": "seller@example.com"
            }
            prop = PropertyCreate(**property_data)
            assert prop.property_type == prop_type
