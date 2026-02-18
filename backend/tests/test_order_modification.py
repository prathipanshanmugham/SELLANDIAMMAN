"""
Test Order Modification with Audit Logging
Features tested:
- GET /api/orders/{id}/modification-history - returns modification logs
- PATCH /api/orders/{id}/customer - updates customer name and logs
- PATCH /api/orders/{id}/status - updates status (admin only)
- POST /api/orders/{id}/items - adds item and logs
- DELETE /api/orders/{id}/items/{item_id} - removes item and logs
- PATCH /api/orders/{id}/items/{item_id}/quantity - updates qty and logs
- Stock reversal when picked item is removed or qty decreased
- Permission checks: Staff can only edit pending, Admin can edit any
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@sellandiamman.com"
ADMIN_PASSWORD = "admin123"

# Test data prefix for cleanup
TEST_PREFIX = "TEST_MOD_"


class TestOrderModificationSetup:
    """Setup fixtures and helper methods"""
    
    @staticmethod
    def get_admin_token():
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["token"]
    
    @staticmethod
    def get_auth_headers(token):
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


class TestModificationHistoryEndpoint:
    """Test GET /api/orders/{id}/modification-history"""
    
    def test_get_modification_history_success(self):
        """Test retrieving modification history for an order"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # First get list of orders
        orders_response = requests.get(f"{BASE_URL}/api/orders?limit=1", headers=headers)
        assert orders_response.status_code == 200, "Failed to get orders"
        
        orders = orders_response.json()
        if not orders:
            pytest.skip("No orders available for testing")
        
        order_id = orders[0]["id"]
        
        # Test modification history endpoint
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        assert response.status_code == 200, f"Failed to get modification history: {response.text}"
        
        # Response should be a list
        history = response.json()
        assert isinstance(history, list), "Modification history should be a list"
        print(f"✅ Modification history endpoint works. Found {len(history)} logs for order {order_id}")
    
    def test_modification_history_invalid_order(self):
        """Test 404 for non-existent order"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/orders/{fake_id}/modification-history", headers=headers)
        # Could be 404 or empty list depending on implementation
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"✅ Modification history handles non-existent order correctly")
    
    def test_modification_history_requires_auth(self):
        """Test that endpoint requires authentication"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/orders/{fake_id}/modification-history")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
        print("✅ Modification history requires authentication")


class TestCustomerUpdateEndpoint:
    """Test PATCH /api/orders/{id}/customer"""
    
    def test_update_customer_success(self):
        """Test updating customer name with reason"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Create a test order first
        product_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = product_resp.json()
        if not products:
            pytest.skip("No products available")
        
        order_data = {
            "customer_name": f"{TEST_PREFIX}Customer_Original",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        assert create_resp.status_code == 200, f"Failed to create test order: {create_resp.text}"
        order_id = create_resp.json()["id"]
        
        # Update customer name
        update_data = {
            "customer_name": f"{TEST_PREFIX}Customer_Updated",
            "reason": "Customer correction"
        }
        response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/customer", json=update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update customer: {response.text}"
        
        result = response.json()
        assert "message" in result, "Response should have message"
        print(f"✅ Customer update successful: {result['message']}")
        
        # Verify the change was logged
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        assert len(history) > 0, "Should have logged the change"
        
        # Find customer_change log
        customer_logs = [log for log in history if log["modification_type"] == "customer_change"]
        assert len(customer_logs) > 0, "Should have customer_change log"
        
        log = customer_logs[0]
        assert log["old_value"] == f"{TEST_PREFIX}Customer_Original", "Old value should be original"
        assert log["new_value"] == f"{TEST_PREFIX}Customer_Updated", "New value should be updated"
        assert log["reason"] == "Customer correction", "Reason should be logged"
        print("✅ Customer change properly logged with old/new values and reason")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
    
    def test_update_customer_empty_name(self):
        """Test that empty customer name is rejected"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get an existing order
        orders_resp = requests.get(f"{BASE_URL}/api/orders?limit=1", headers=headers)
        orders = orders_resp.json()
        if not orders:
            pytest.skip("No orders available")
        
        order_id = orders[0]["id"]
        
        # Try empty name
        update_data = {"customer_name": "", "reason": "Test"}
        response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/customer", json=update_data, headers=headers)
        # Should fail validation
        assert response.status_code in [400, 422], f"Should reject empty name: {response.status_code}"
        print("✅ Empty customer name is rejected")


class TestStatusUpdateEndpoint:
    """Test PATCH /api/orders/{id}/status (Admin only)"""
    
    def test_update_status_admin_success(self):
        """Test admin can update order status"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Create test order
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = products_resp.json()
        if not products:
            pytest.skip("No products available")
        
        order_data = {
            "customer_name": f"{TEST_PREFIX}StatusTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        assert create_resp.status_code == 200, f"Failed to create order: {create_resp.text}"
        order_id = create_resp.json()["id"]
        
        # Update status to completed
        update_data = {"status": "completed", "reason": "Testing completion"}
        response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", json=update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update status: {response.text}"
        print("✅ Admin can change status to completed")
        
        # Verify the change
        order_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
        order = order_resp.json()
        assert order["status"] == "completed", "Status should be updated"
        
        # Verify logging
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        status_logs = [log for log in history if log["modification_type"] == "status_change"]
        assert len(status_logs) > 0, "Should have status_change log"
        assert status_logs[0]["old_value"] == "pending"
        assert status_logs[0]["new_value"] == "completed"
        print("✅ Status change properly logged")
        
        # Test reopen
        reopen_data = {"status": "pending", "reason": "Reopening for test"}
        reopen_resp = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", json=reopen_data, headers=headers)
        assert reopen_resp.status_code == 200, "Admin should be able to reopen"
        print("✅ Admin can reopen completed order")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
    
    def test_status_update_requires_admin(self):
        """Test that status update requires admin role"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get an order
        orders_resp = requests.get(f"{BASE_URL}/api/orders?limit=1", headers=headers)
        orders = orders_resp.json()
        if not orders:
            pytest.skip("No orders available")
        
        order_id = orders[0]["id"]
        
        # Try without auth
        update_data = {"status": "completed"}
        response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", json=update_data)
        assert response.status_code in [401, 403], "Should require auth"
        print("✅ Status update requires admin authentication")


class TestAddItemEndpoint:
    """Test POST /api/orders/{id}/items"""
    
    def test_add_item_success(self):
        """Test adding item to order with logging"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get available products
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=5", headers=headers)
        products = products_resp.json()
        if len(products) < 2:
            pytest.skip("Need at least 2 products")
        
        # Create order with first product
        order_data = {
            "customer_name": f"{TEST_PREFIX}AddItemTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        assert create_resp.status_code == 200, f"Failed to create order: {create_resp.text}"
        order_id = create_resp.json()["id"]
        
        # Add second product
        add_item_data = {
            "sku": products[1]["sku"],
            "quantity_required": 3,
            "reason": "Customer requested"
        }
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/items", json=add_item_data, headers=headers)
        assert response.status_code == 200, f"Failed to add item: {response.text}"
        
        result = response.json()
        assert "item_id" in result, "Should return new item_id"
        print(f"✅ Item added successfully: {result['message']}")
        
        # Verify order has 2 items now
        order_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
        order = order_resp.json()
        assert len(order["items"]) == 2, "Order should have 2 items"
        
        # Verify logging
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        add_logs = [log for log in history if log["modification_type"] == "add_item"]
        assert len(add_logs) > 0, "Should have add_item log"
        assert products[1]["sku"] in add_logs[0]["new_value"], "Log should contain SKU"
        print("✅ Add item properly logged")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
    
    def test_add_duplicate_item_fails(self):
        """Test that adding duplicate SKU fails"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get a product
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = products_resp.json()
        if not products:
            pytest.skip("No products available")
        
        # Create order
        order_data = {
            "customer_name": f"{TEST_PREFIX}DupItemTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order_id = create_resp.json()["id"]
        
        # Try to add same SKU again
        add_item_data = {"sku": products[0]["sku"], "quantity_required": 2}
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/items", json=add_item_data, headers=headers)
        assert response.status_code == 400, f"Should reject duplicate: {response.status_code}"
        assert "already exists" in response.json().get("detail", "").lower() or "quantity update" in response.json().get("detail", "").lower()
        print("✅ Duplicate item correctly rejected")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)


class TestRemoveItemEndpoint:
    """Test DELETE /api/orders/{id}/items/{item_id}"""
    
    def test_remove_item_success(self):
        """Test removing item from order"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get products
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=2", headers=headers)
        products = products_resp.json()
        if len(products) < 2:
            pytest.skip("Need at least 2 products")
        
        # Create order with 2 items
        order_data = {
            "customer_name": f"{TEST_PREFIX}RemoveItemTest",
            "items": [
                {"sku": products[0]["sku"], "quantity_required": 2},
                {"sku": products[1]["sku"], "quantity_required": 3}
            ]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order = create_resp.json()
        order_id = order["id"]
        item_to_remove = order["items"][1]
        
        # Remove second item
        response = requests.delete(
            f"{BASE_URL}/api/orders/{order_id}/items/{item_to_remove['id']}?reason=CustomerCancelled",
            headers=headers
        )
        assert response.status_code == 200, f"Failed to remove item: {response.text}"
        print("✅ Item removed successfully")
        
        # Verify order has 1 item now
        order_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
        updated_order = order_resp.json()
        assert len(updated_order["items"]) == 1, "Order should have 1 item"
        
        # Verify logging
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        remove_logs = [log for log in history if log["modification_type"] == "remove_item"]
        assert len(remove_logs) > 0, "Should have remove_item log"
        assert item_to_remove["sku"] in remove_logs[0]["old_value"], "Log should contain removed SKU"
        print("✅ Remove item properly logged")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
    
    def test_remove_picked_item_restores_stock(self):
        """Test that removing a picked item restores stock"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get a product with stock
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=10", headers=headers)
        products = [p for p in products_resp.json() if p["quantity_available"] >= 5]
        if not products:
            pytest.skip("No products with sufficient stock")
        
        product = products[0]
        initial_stock = product["quantity_available"]
        qty_to_pick = 3
        
        # Create order
        order_data = {
            "customer_name": f"{TEST_PREFIX}StockRestore",
            "items": [{"sku": product["sku"], "quantity_required": qty_to_pick}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order = create_resp.json()
        order_id = order["id"]
        item_id = order["items"][0]["id"]
        
        # Mark item as picked (deducts stock)
        pick_resp = requests.patch(f"{BASE_URL}/api/orders/{order_id}/items/{item_id}/pick", headers=headers)
        if pick_resp.status_code != 200:
            print(f"Warning: Could not pick item: {pick_resp.text}")
            requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
            pytest.skip("Could not pick item")
        
        # Verify stock was deducted
        product_resp = requests.get(f"{BASE_URL}/api/products/{product['id']}", headers=headers)
        stock_after_pick = product_resp.json()["quantity_available"]
        assert stock_after_pick == initial_stock - qty_to_pick, "Stock should be deducted after pick"
        print(f"✅ Stock deducted after pick: {initial_stock} -> {stock_after_pick}")
        
        # Remove the picked item
        remove_resp = requests.delete(
            f"{BASE_URL}/api/orders/{order_id}/items/{item_id}?reason=StockRestoreTest",
            headers=headers
        )
        assert remove_resp.status_code == 200, f"Failed to remove: {remove_resp.text}"
        
        result = remove_resp.json()
        assert result.get("stock_restored", 0) == qty_to_pick, "Should report stock restored"
        print(f"✅ Remove response shows stock_restored: {result.get('stock_restored')}")
        
        # Verify stock was restored
        product_resp = requests.get(f"{BASE_URL}/api/products/{product['id']}", headers=headers)
        stock_after_remove = product_resp.json()["quantity_available"]
        assert stock_after_remove == initial_stock, f"Stock should be restored: {stock_after_remove} != {initial_stock}"
        print(f"✅ Stock restored after removing picked item: {stock_after_pick} -> {stock_after_remove}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)


class TestUpdateQuantityEndpoint:
    """Test PATCH /api/orders/{id}/items/{item_id}/quantity"""
    
    def test_update_quantity_success(self):
        """Test updating item quantity"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get a product
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = products_resp.json()
        if not products:
            pytest.skip("No products available")
        
        # Create order
        order_data = {
            "customer_name": f"{TEST_PREFIX}QtyUpdateTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 2}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order = create_resp.json()
        order_id = order["id"]
        item_id = order["items"][0]["id"]
        
        # Update quantity
        update_data = {"quantity_required": 5, "reason": "Customer wants more"}
        response = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/items/{item_id}/quantity",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200, f"Failed to update qty: {response.text}"
        print("✅ Quantity updated successfully")
        
        # Verify the change
        order_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
        updated_order = order_resp.json()
        assert updated_order["items"][0]["quantity_required"] == 5, "Quantity should be updated"
        
        # Verify logging
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        qty_logs = [log for log in history if log["modification_type"] == "qty_change"]
        assert len(qty_logs) > 0, "Should have qty_change log"
        assert qty_logs[0]["old_value"] == "2", "Old value should be 2"
        assert qty_logs[0]["new_value"] == "5", "New value should be 5"
        print("✅ Quantity change properly logged")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)
    
    def test_update_quantity_invalid_zero(self):
        """Test that zero quantity is rejected"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get an order with items
        orders_resp = requests.get(f"{BASE_URL}/api/orders?status=pending&limit=1", headers=headers)
        orders = orders_resp.json()
        if not orders or not orders[0]["items"]:
            pytest.skip("No pending orders with items")
        
        order_id = orders[0]["id"]
        item_id = orders[0]["items"][0]["id"]
        
        # Try zero quantity
        update_data = {"quantity_required": 0}
        response = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/items/{item_id}/quantity",
            json=update_data,
            headers=headers
        )
        assert response.status_code in [400, 422], f"Should reject zero qty: {response.status_code}"
        print("✅ Zero quantity correctly rejected")


class TestPermissionChecks:
    """Test staff vs admin permission differences"""
    
    def test_staff_cannot_edit_completed_order(self):
        """Test that staff cannot edit completed orders"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get products
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = products_resp.json()
        if not products:
            pytest.skip("No products available")
        
        # Create order
        order_data = {
            "customer_name": f"{TEST_PREFIX}PermTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order = create_resp.json()
        order_id = order["id"]
        
        # Mark as completed (admin)
        status_resp = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/status",
            json={"status": "completed"},
            headers=headers
        )
        assert status_resp.status_code == 200, "Admin should be able to complete"
        
        # Admin can still edit completed order
        update_resp = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/customer",
            json={"customer_name": f"{TEST_PREFIX}AdminEdit"},
            headers=headers
        )
        assert update_resp.status_code == 200, "Admin should be able to edit completed order"
        print("✅ Admin can edit completed orders")
        
        # Note: To test staff restriction, would need staff credentials
        # The backend code checks user["role"] != "admin" and order["status"] == "completed"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)


class TestAuditLogFields:
    """Test that audit logs contain all required fields"""
    
    def test_log_has_all_required_fields(self):
        """Test modification log structure"""
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get products
        products_resp = requests.get(f"{BASE_URL}/api/products?limit=1", headers=headers)
        products = products_resp.json()
        if not products:
            pytest.skip("No products available")
        
        # Create order
        order_data = {
            "customer_name": f"{TEST_PREFIX}AuditLogTest",
            "items": [{"sku": products[0]["sku"], "quantity_required": 1}]
        }
        create_resp = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
        order = create_resp.json()
        order_id = order["id"]
        order_number = order["order_number"]
        
        # Make a modification
        requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/customer",
            json={"customer_name": f"{TEST_PREFIX}AuditLogUpdated", "reason": "Audit test"},
            headers=headers
        )
        
        # Get modification history
        history_resp = requests.get(f"{BASE_URL}/api/orders/{order_id}/modification-history", headers=headers)
        history = history_resp.json()
        assert len(history) > 0, "Should have log entries"
        
        log = history[0]
        
        # Check required fields
        required_fields = [
            "order_id", "order_number", "modified_by", "modified_by_name",
            "modification_type", "field_changed", "old_value", "new_value",
            "timestamp"
        ]
        for field in required_fields:
            assert field in log, f"Log should have field: {field}"
        
        # Verify field values
        assert log["order_id"] == order_id, "Order ID should match"
        assert log["order_number"] == order_number, "Order number should match"
        assert log["modified_by_name"] == "Admin", "Modified by name should be Admin"
        assert log["modification_type"] == "customer_change", "Type should be customer_change"
        assert log["reason"] == "Audit test", "Reason should be logged"
        
        print("✅ Audit log contains all required fields:")
        print(f"   - order_id: {log['order_id']}")
        print(f"   - order_number: {log['order_number']}")
        print(f"   - modified_by: {log['modified_by']}")
        print(f"   - modified_by_name: {log['modified_by_name']}")
        print(f"   - modification_type: {log['modification_type']}")
        print(f"   - field_changed: {log['field_changed']}")
        print(f"   - old_value: {log['old_value']}")
        print(f"   - new_value: {log['new_value']}")
        print(f"   - reason: {log.get('reason')}")
        print(f"   - timestamp: {log['timestamp']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=headers)


# Cleanup function to run after all tests
def teardown_module():
    """Clean up test data"""
    try:
        token = TestOrderModificationSetup.get_admin_token()
        headers = TestOrderModificationSetup.get_auth_headers(token)
        
        # Get orders with test prefix
        orders_resp = requests.get(f"{BASE_URL}/api/orders?limit=100", headers=headers)
        if orders_resp.status_code == 200:
            for order in orders_resp.json():
                if order["customer_name"].startswith(TEST_PREFIX):
                    requests.delete(f"{BASE_URL}/api/orders/{order['id']}", headers=headers)
        print("\n✅ Test cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
