"""
Backend API Tests for Price and Catalogue Features
Tests: Price fields in products, public catalogue hiding stock/location, product form with pricing
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://inventory-mobile-fix.preview.emergentagent.com').rstrip('/')

class TestPublicCatalogue:
    """Test public catalogue API - should show prices but NOT stock/location"""
    
    def test_public_catalogue_returns_price_fields(self):
        """Public catalogue should return selling_price, mrp, unit fields"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?limit=10")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) > 0
        
        # Check that price fields are present
        for product in products:
            assert "selling_price" in product, f"Missing selling_price for {product.get('sku')}"
            assert "mrp" in product, f"Missing mrp for {product.get('sku')}"
            assert "unit" in product, f"Missing unit for {product.get('sku')}"
            assert isinstance(product["selling_price"], (int, float)), "selling_price should be numeric"
            assert isinstance(product["mrp"], (int, float)), "mrp should be numeric"
            assert isinstance(product["unit"], str), "unit should be string"
    
    def test_public_catalogue_hides_stock_and_location(self):
        """Public catalogue should NOT expose stock quantity or location codes"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?limit=10")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) > 0
        
        for product in products:
            # These sensitive fields should NOT be exposed
            assert "quantity_available" not in product, f"quantity_available should be hidden for {product.get('sku')}"
            assert "full_location_code" not in product, f"full_location_code should be hidden for {product.get('sku')}"
            assert "zone" not in product, f"zone should be hidden for {product.get('sku')}"
            assert "aisle" not in product, f"aisle should be hidden for {product.get('sku')}"
            assert "rack" not in product, f"rack should be hidden for {product.get('sku')}"
            assert "shelf" not in product, f"shelf should be hidden for {product.get('sku')}"
            assert "bin" not in product, f"bin should be hidden for {product.get('sku')}"
            assert "reorder_level" not in product, f"reorder_level should be hidden for {product.get('sku')}"
            assert "supplier" not in product, f"supplier should be hidden for {product.get('sku')}"
    
    def test_public_catalogue_returns_basic_product_info(self):
        """Public catalogue should have basic product info"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?limit=5")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) > 0
        
        for product in products:
            assert "sku" in product
            assert "product_name" in product
            assert "category" in product
            assert "brand" in product
            assert "image_url" in product
    
    def test_wire001_has_correct_pricing(self):
        """WIRE001 should have selling_price=85, mrp=100, unit=meter"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?search=WIRE001")
        assert response.status_code == 200
        
        products = response.json()
        wire_product = next((p for p in products if p["sku"] == "WIRE001"), None)
        
        assert wire_product is not None, "WIRE001 should exist"
        assert wire_product["selling_price"] == 85.0, f"Expected 85, got {wire_product['selling_price']}"
        assert wire_product["mrp"] == 100.0, f"Expected 100, got {wire_product['mrp']}"
        assert wire_product["unit"] == "meter", f"Expected 'meter', got {wire_product['unit']}"
    
    def test_mcb001_has_correct_pricing(self):
        """MCB001 should have selling_price=450, mrp=550, unit=piece"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?search=MCB001")
        assert response.status_code == 200
        
        products = response.json()
        mcb_product = next((p for p in products if p["sku"] == "MCB001"), None)
        
        assert mcb_product is not None, "MCB001 should exist"
        assert mcb_product["selling_price"] == 450.0, f"Expected 450, got {mcb_product['selling_price']}"
        assert mcb_product["mrp"] == 550.0, f"Expected 550, got {mcb_product['mrp']}"
        assert mcb_product["unit"] == "piece"
    
    def test_drill01_has_correct_pricing(self):
        """DRILL01 should have selling_price=2499, mrp=2999, unit=piece"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?search=DRILL01")
        assert response.status_code == 200
        
        products = response.json()
        drill_product = next((p for p in products if p["sku"] == "DRILL01"), None)
        
        assert drill_product is not None, "DRILL01 should exist"
        assert drill_product["selling_price"] == 2499.0
        assert drill_product["mrp"] == 2999.0
        assert drill_product["unit"] == "piece"
    
    def test_products_with_zero_price(self):
        """Products with selling_price=0 should show 'Price on request' scenario"""
        response = requests.get(f"{BASE_URL}/api/public/catalogue?limit=50")
        assert response.status_code == 200
        
        products = response.json()
        zero_price_products = [p for p in products if p["selling_price"] == 0]
        
        # There should be some products with zero price
        assert len(zero_price_products) > 0, "Should have products with selling_price=0"
        
        for product in zero_price_products:
            assert product["selling_price"] == 0, f"Expected 0 for {product['sku']}"


class TestAuthenticatedProductAPI:
    """Test authenticated product API - should have full details including price fields"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_authenticated_products_have_all_price_fields(self, auth_token):
        """Authenticated API should return all price fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/products?limit=5", headers=headers)
        
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        
        for product in products:
            # Price fields
            assert "selling_price" in product, f"Missing selling_price for {product.get('sku')}"
            assert "mrp" in product, f"Missing mrp for {product.get('sku')}"
            assert "unit" in product, f"Missing unit for {product.get('sku')}"
            assert "gst_percentage" in product, f"Missing gst_percentage for {product.get('sku')}"
            
            # Location fields (should be present for authenticated users)
            assert "full_location_code" in product
            assert "quantity_available" in product
            assert "zone" in product
    
    def test_create_product_with_pricing(self, auth_token):
        """Test creating a product with all pricing fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        test_product = {
            "sku": "TEST_PRICE001",
            "product_name": "Test Product with Pricing",
            "category": "Test",
            "brand": "Test Brand",
            "zone": "T",
            "aisle": 1,
            "rack": 1,
            "shelf": 1,
            "bin": 1,
            "quantity_available": 50,
            "reorder_level": 10,
            "supplier": "Test Supplier",
            "image_url": "",
            "selling_price": 125.50,
            "mrp": 150.00,
            "unit": "meter",
            "gst_percentage": 12
        }
        
        # Create product
        response = requests.post(f"{BASE_URL}/api/products", json=test_product, headers=headers)
        
        if response.status_code == 400 and "already exists" in response.text:
            # Product already exists from previous test, delete and retry
            products = requests.get(f"{BASE_URL}/api/products?search=TEST_PRICE001", headers=headers).json()
            if products:
                requests.delete(f"{BASE_URL}/api/products/{products[0]['id']}", headers=headers)
                response = requests.post(f"{BASE_URL}/api/products", json=test_product, headers=headers)
        
        assert response.status_code in [200, 201], f"Failed to create product: {response.text}"
        
        created = response.json()
        assert created["selling_price"] == 125.50
        assert created["mrp"] == 150.00
        assert created["unit"] == "meter"
        assert created["gst_percentage"] == 12
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/products/{created['id']}", headers=headers)
    
    def test_update_product_pricing(self, auth_token):
        """Test updating product pricing fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create a test product
        test_product = {
            "sku": "TEST_UPDATE001",
            "product_name": "Test Update Product",
            "category": "Test",
            "brand": "Test",
            "zone": "T",
            "aisle": 2,
            "rack": 2,
            "shelf": 1,
            "bin": 1,
            "quantity_available": 10,
            "reorder_level": 5,
            "supplier": "",
            "image_url": "",
            "selling_price": 100.0,
            "mrp": 120.0,
            "unit": "piece",
            "gst_percentage": 18
        }
        
        # Create or find existing
        response = requests.post(f"{BASE_URL}/api/products", json=test_product, headers=headers)
        if response.status_code == 400:
            products = requests.get(f"{BASE_URL}/api/products?search=TEST_UPDATE001", headers=headers).json()
            if products:
                product_id = products[0]["id"]
            else:
                pytest.skip("Could not create or find test product")
        else:
            product_id = response.json()["id"]
        
        # Update pricing
        test_product["selling_price"] = 200.0
        test_product["mrp"] = 250.0
        test_product["unit"] = "box"
        test_product["gst_percentage"] = 5
        
        update_response = requests.put(f"{BASE_URL}/api/products/{product_id}", json=test_product, headers=headers)
        assert update_response.status_code == 200
        
        updated = update_response.json()
        assert updated["selling_price"] == 200.0
        assert updated["mrp"] == 250.0
        assert updated["unit"] == "box"
        assert updated["gst_percentage"] == 5
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/products/{product_id}", headers=headers)


class TestOrdersWithPricing:
    """Test that orders still work correctly with new pricing fields"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_orders_endpoint_works(self, auth_token):
        """Orders API should still function"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/orders?limit=5", headers=headers)
        
        assert response.status_code == 200
        orders = response.json()
        
        # Verify order structure
        if len(orders) > 0:
            order = orders[0]
            assert "order_number" in order
            assert "customer_name" in order
            assert "items" in order
            
            # Verify items have location for picklist
            for item in order["items"]:
                assert "full_location_code" in item
                assert "quantity_required" in item
                assert "sku" in item


class TestCompactReceiptFormat:
    """Test that order data supports compact receipt format"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_order_has_all_picklist_fields(self, auth_token):
        """Order should have all fields needed for compact picklist"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get an existing order or create one
        orders_response = requests.get(f"{BASE_URL}/api/orders?limit=1", headers=headers)
        assert orders_response.status_code == 200
        
        orders = orders_response.json()
        
        if len(orders) > 0:
            order = orders[0]
            
            # Check order has fields for compact receipt header
            assert "order_number" in order
            assert "customer_name" in order
            assert "created_at" in order
            
            # Check items have fields for compact one-line format
            for item in order["items"]:
                assert "product_name" in item, "Item should have product_name for display"
                assert "full_location_code" in item, "Item should have full_location_code for location"
                assert "quantity_required" in item, "Item should have quantity_required"
                assert "sku" in item, "Item should have sku"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
