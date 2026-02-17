"""
Backend tests for:
1) Order ID Input + Auto Sequence (ORD-0001, ORD-0002...)
2) POS Printing - verified via CSS in frontend (no backend test needed)
3) Master QR Code - verified via frontend (QR data generation)

Tests cover:
- GET /api/orders/next-order-id returns next sequential order ID
- POST /api/orders accepts optional order_id parameter
- POST /api/orders rejects duplicate order_id
- POST /api/orders auto-generates if order_id not provided
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestNextOrderIdEndpoint:
    """Test GET /api/orders/next-order-id endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_next_order_id_endpoint_exists(self):
        """Test that /api/orders/next-order-id returns 200"""
        response = requests.get(f"{BASE_URL}/api/orders/next-order-id", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✅ GET /api/orders/next-order-id returns 200")
    
    def test_next_order_id_format(self):
        """Test that next_order_id is in ORD-0001 format"""
        response = requests.get(f"{BASE_URL}/api/orders/next-order-id", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "next_order_id" in data, f"Response missing 'next_order_id' field: {data}"
        
        next_id = data["next_order_id"]
        # Check format: ORD-XXXX where XXXX is 4 digits
        assert next_id.startswith("ORD-"), f"Expected ORD- prefix, got: {next_id}"
        assert len(next_id) == 8, f"Expected 8 chars (ORD-XXXX), got {len(next_id)}: {next_id}"
        
        # Verify digits part
        digits_part = next_id[4:]
        assert digits_part.isdigit(), f"Expected 4 digits after ORD-, got: {digits_part}"
        
        print(f"✅ next_order_id format correct: {next_id}")
    
    def test_next_order_id_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/orders/next-order-id")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✅ /api/orders/next-order-id requires authentication")


class TestOrderCreateWithCustomId:
    """Test POST /api/orders with optional order_id parameter"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token, setup test SKU"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Get or create a test product for orders
        products_resp = requests.get(f"{BASE_URL}/api/products", headers=self.headers)
        if products_resp.status_code == 200 and len(products_resp.json()) > 0:
            self.test_sku = products_resp.json()[0]["sku"]
        else:
            # Create a test product
            product_data = {
                "sku": "TEST-SKU-001",
                "product_name": "Test Product",
                "category": "Test",
                "zone": "A",
                "aisle": 1,
                "rack": 1,
                "shelf": 1,
                "bin": 1,
                "quantity_available": 100,
                "reorder_level": 10
            }
            create_resp = requests.post(f"{BASE_URL}/api/products", json=product_data, headers=self.headers)
            self.test_sku = "TEST-SKU-001"
        
        self.created_order_ids = []
    
    def teardown_method(self, method):
        """Cleanup created orders"""
        for order_id in self.created_order_ids:
            try:
                requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=self.headers)
            except:
                pass
    
    def test_create_order_with_custom_id(self):
        """Test creating order with custom order_id"""
        import time
        custom_id = f"CUSTOM-{int(time.time())}"
        
        order_data = {
            "customer_name": "Test Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": custom_id
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        self.created_order_ids.append(data["id"])
        
        assert data["order_number"] == custom_id.upper(), f"Expected {custom_id.upper()}, got {data['order_number']}"
        print(f"✅ Order created with custom ID: {data['order_number']}")
    
    def test_create_order_without_order_id_auto_generates(self):
        """Test creating order without order_id auto-generates ORD-XXXX"""
        order_data = {
            "customer_name": "Test Auto-Gen Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}]
            # No order_id provided
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        self.created_order_ids.append(data["id"])
        
        order_number = data["order_number"]
        assert order_number.startswith("ORD-"), f"Expected ORD- prefix, got: {order_number}"
        print(f"✅ Order auto-generated ID: {order_number}")
    
    def test_create_order_with_empty_order_id_auto_generates(self):
        """Test creating order with empty string order_id auto-generates"""
        order_data = {
            "customer_name": "Test Empty ID Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": ""  # Empty string should trigger auto-generate
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        self.created_order_ids.append(data["id"])
        
        order_number = data["order_number"]
        assert order_number.startswith("ORD-"), f"Expected ORD- prefix for empty order_id, got: {order_number}"
        print(f"✅ Empty order_id auto-generated: {order_number}")
    
    def test_create_order_with_null_order_id_auto_generates(self):
        """Test creating order with null order_id auto-generates"""
        order_data = {
            "customer_name": "Test Null ID Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": None  # Null should trigger auto-generate
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        self.created_order_ids.append(data["id"])
        
        order_number = data["order_number"]
        assert order_number.startswith("ORD-"), f"Expected ORD- prefix for null order_id, got: {order_number}"
        print(f"✅ Null order_id auto-generated: {order_number}")
    
    def test_create_order_rejects_duplicate_id(self):
        """Test creating order with duplicate order_id is rejected"""
        import time
        unique_id = f"DUP-{int(time.time())}"
        
        # Create first order
        order_data = {
            "customer_name": "First Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": unique_id
        }
        
        response1 = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response1.status_code == 200, f"First order creation failed: {response1.text}"
        self.created_order_ids.append(response1.json()["id"])
        
        # Try to create second order with same ID
        order_data2 = {
            "customer_name": "Second Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": unique_id  # Same ID as first order
        }
        
        response2 = requests.post(f"{BASE_URL}/api/orders", json=order_data2, headers=self.headers)
        assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}: {response2.text}"
        
        error_msg = response2.json().get("detail", "")
        assert "already exists" in error_msg.lower(), f"Expected 'already exists' error, got: {error_msg}"
        print(f"✅ Duplicate order_id rejected: {unique_id}")
    
    def test_order_id_converted_to_uppercase(self):
        """Test that custom order_id is converted to uppercase"""
        import time
        lowercase_id = f"lowercase-{int(time.time())}"
        
        order_data = {
            "customer_name": "Lowercase Test Customer",
            "items": [{"sku": self.test_sku, "quantity_required": 1}],
            "order_id": lowercase_id
        }
        
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        self.created_order_ids.append(data["id"])
        
        assert data["order_number"] == lowercase_id.upper(), f"Expected uppercase {lowercase_id.upper()}, got {data['order_number']}"
        print(f"✅ Order ID converted to uppercase: {data['order_number']}")


class TestSequentialOrderIdGeneration:
    """Test sequential order ID generation (ORD-0001, ORD-0002...)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Get test SKU
        products_resp = requests.get(f"{BASE_URL}/api/products", headers=self.headers)
        if products_resp.status_code == 200 and len(products_resp.json()) > 0:
            self.test_sku = products_resp.json()[0]["sku"]
        else:
            self.test_sku = "TEST-SKU-001"
        
        self.created_order_ids = []
    
    def teardown_method(self, method):
        """Cleanup created orders"""
        for order_id in self.created_order_ids:
            try:
                requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=self.headers)
            except:
                pass
    
    def test_sequential_order_generation(self):
        """Test that two consecutive orders get sequential numbers"""
        # Get next ID
        resp1 = requests.get(f"{BASE_URL}/api/orders/next-order-id", headers=self.headers)
        next_id_1 = resp1.json()["next_order_id"]
        num_1 = int(next_id_1[4:])  # Extract number from ORD-XXXX
        
        # Create order using auto-generated ID
        order_data = {
            "customer_name": "Sequential Test Customer 1",
            "items": [{"sku": self.test_sku, "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=self.headers)
        assert create_resp.status_code == 200
        created_order = create_resp.json()
        self.created_order_ids.append(created_order["id"])
        
        # Get next ID again
        resp2 = requests.get(f"{BASE_URL}/api/orders/next-order-id", headers=self.headers)
        next_id_2 = resp2.json()["next_order_id"]
        num_2 = int(next_id_2[4:])
        
        # The next ID after creation should be higher
        assert num_2 > num_1, f"Expected sequential increase: {next_id_1} -> {next_id_2}"
        print(f"✅ Sequential order ID generation: {next_id_1} -> created -> next is {next_id_2}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
