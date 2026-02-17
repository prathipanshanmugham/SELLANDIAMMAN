"""
Test cases for new features:
1. Staff Presence System - Admin can set/view staff presence status
2. QR Code data structure validation (backend provides order data for QR generation)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Get auth token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        return data["token"]
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Return headers with admin auth token"""
        return {"Authorization": f"Bearer {admin_token}"}


class TestStaffPresenceAPI(TestAuth):
    """Tests for Staff Presence System - GET /api/dashboard/staff-presence, PATCH /api/employees/{id}/presence, GET /api/employees/presence-log"""
    
    def test_get_staff_presence_returns_list(self, admin_headers):
        """GET /api/dashboard/staff-presence should return list of staff with presence status"""
        response = requests.get(f"{BASE_URL}/api/dashboard/staff-presence", headers=admin_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list), "Expected list of staff members"
        
        # If there are staff members, check structure
        if len(data) > 0:
            staff = data[0]
            assert "id" in staff, "Staff should have id"
            assert "name" in staff, "Staff should have name"
            assert "role" in staff, "Staff should have role"
            assert "presence_status" in staff, "Staff should have presence_status"
            
            # Presence status should be valid
            valid_statuses = ["present", "permission", "on_field", "absent", "on_leave"]
            assert staff["presence_status"] in valid_statuses, f"Invalid presence status: {staff['presence_status']}"
            print(f"✅ Found {len(data)} staff members with presence data")
    
    def test_update_staff_presence_status(self, admin_headers):
        """PATCH /api/employees/{id}/presence should update staff presence status"""
        # First get list of staff
        response = requests.get(f"{BASE_URL}/api/dashboard/staff-presence", headers=admin_headers)
        assert response.status_code == 200
        staff_list = response.json()
        
        assert len(staff_list) > 0, "No staff members found to test"
        
        staff = staff_list[0]
        staff_id = staff["id"]
        original_status = staff["presence_status"]
        
        # Test all 5 presence statuses
        test_statuses = ["present", "permission", "on_field", "absent", "on_leave"]
        
        for new_status in test_statuses:
            response = requests.patch(
                f"{BASE_URL}/api/employees/{staff_id}/presence",
                json={"presence_status": new_status},
                headers=admin_headers
            )
            
            assert response.status_code == 200, f"Expected 200 for {new_status}, got {response.status_code}: {response.text}"
            print(f"✅ Successfully set presence to: {new_status}")
        
        # Verify the status was updated
        response = requests.get(f"{BASE_URL}/api/dashboard/staff-presence", headers=admin_headers)
        assert response.status_code == 200
        updated_staff = next((s for s in response.json() if s["id"] == staff_id), None)
        
        assert updated_staff is not None, "Staff member not found after update"
        assert updated_staff["presence_status"] == "on_leave", f"Expected 'on_leave', got: {updated_staff['presence_status']}"
        
        # Reset to original status
        requests.patch(
            f"{BASE_URL}/api/employees/{staff_id}/presence",
            json={"presence_status": original_status},
            headers=admin_headers
        )
        print(f"✅ Status change persistence verified")
    
    def test_update_presence_invalid_status(self, admin_headers):
        """PATCH /api/employees/{id}/presence should reject invalid status"""
        response = requests.get(f"{BASE_URL}/api/dashboard/staff-presence", headers=admin_headers)
        staff_list = response.json()
        
        if len(staff_list) > 0:
            staff_id = staff_list[0]["id"]
            
            response = requests.patch(
                f"{BASE_URL}/api/employees/{staff_id}/presence",
                json={"presence_status": "invalid_status"},
                headers=admin_headers
            )
            
            # Should fail validation (422 Unprocessable Entity)
            assert response.status_code == 422, f"Expected 422 for invalid status, got {response.status_code}"
            print("✅ Invalid status correctly rejected with 422")
    
    def test_update_presence_nonexistent_employee(self, admin_headers):
        """PATCH /api/employees/{id}/presence should return 404 for nonexistent employee"""
        response = requests.patch(
            f"{BASE_URL}/api/employees/nonexistent-id-12345/presence",
            json={"presence_status": "present"},
            headers=admin_headers
        )
        
        assert response.status_code == 404, f"Expected 404 for nonexistent employee, got {response.status_code}"
        print("✅ Nonexistent employee correctly returns 404")
    
    def test_get_presence_log(self, admin_headers):
        """GET /api/employees/presence-log should return status change history"""
        response = requests.get(f"{BASE_URL}/api/employees/presence-log", headers=admin_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list), "Expected list of log entries"
        
        # If there are entries, check structure
        if len(data) > 0:
            log = data[0]
            assert "employee_id" in log, "Log should have employee_id"
            assert "employee_name" in log, "Log should have employee_name"
            assert "previous_status" in log, "Log should have previous_status"
            assert "new_status" in log, "Log should have new_status"
            assert "changed_by" in log, "Log should have changed_by"
            assert "changed_by_name" in log, "Log should have changed_by_name"
            assert "timestamp" in log, "Log should have timestamp"
            print(f"✅ Presence log contains {len(data)} entries with proper structure")
        else:
            print("✅ Presence log endpoint works (empty list - no changes yet)")


class TestOrderQRCodeData(TestAuth):
    """Tests for QR Code data - verify order API returns data suitable for QR code generation"""
    
    def test_order_contains_qr_data_fields(self, admin_headers):
        """GET /api/orders/{id} should return data fields needed for QR code"""
        # First get list of orders
        response = requests.get(f"{BASE_URL}/api/orders", headers=admin_headers)
        assert response.status_code == 200
        orders = response.json()
        
        if len(orders) == 0:
            # Create a test order if none exists
            print("No orders exist, creating a test order...")
            
            # Get a product first
            products_resp = requests.get(f"{BASE_URL}/api/products", headers=admin_headers)
            if products_resp.status_code == 200 and len(products_resp.json()) > 0:
                product = products_resp.json()[0]
                
                # Create order
                order_resp = requests.post(f"{BASE_URL}/api/orders", json={
                    "customer_name": "TEST_QR_Customer",
                    "items": [{"sku": product["sku"], "quantity_required": 1}]
                }, headers=admin_headers)
                
                if order_resp.status_code in [200, 201]:
                    orders = [order_resp.json()]
                else:
                    pytest.skip("Could not create test order")
            else:
                pytest.skip("No products available to create order")
        
        # Check an order has required fields for QR code
        order = orders[0]
        order_id = order["id"]
        
        # Get single order
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}", headers=admin_headers)
        assert response.status_code == 200
        order_data = response.json()
        
        # Verify fields needed for QR code JSON: {order_id, customer, items: [{sku, qty}]}
        assert "order_number" in order_data, "Order should have order_number for QR"
        assert "customer_name" in order_data, "Order should have customer_name for QR"
        assert "items" in order_data, "Order should have items for QR"
        assert isinstance(order_data["items"], list), "items should be a list"
        
        if len(order_data["items"]) > 0:
            item = order_data["items"][0]
            assert "sku" in item, "Item should have sku for QR"
            assert "quantity_required" in item, "Item should have quantity_required for QR"
        
        print(f"✅ Order {order_data['order_number']} has all fields needed for QR code:")
        print(f"   - order_number: {order_data['order_number']}")
        print(f"   - customer_name: {order_data['customer_name']}")
        print(f"   - items count: {len(order_data['items'])}")
        
        # Verify the JSON structure matches what frontend expects
        qr_data = {
            "order_id": order_data["order_number"],
            "customer": order_data["customer_name"],
            "items": [{"sku": item["sku"], "qty": item["quantity_required"]} for item in order_data["items"]]
        }
        
        # Ensure it can be serialized
        import json
        json_str = json.dumps(qr_data)
        assert len(json_str) > 0, "QR data should be serializable to JSON"
        print(f"✅ QR JSON structure is valid: {len(json_str)} characters")


class TestDashboardEndpoints(TestAuth):
    """Additional dashboard endpoint tests"""
    
    def test_dashboard_stats(self, admin_headers):
        """GET /api/dashboard/stats should return dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_products" in data
        assert "total_stock_units" in data
        assert "low_stock_items" in data
        assert "sales_today" in data
        assert "orders_pending" in data
        assert "orders_completed" in data
        print(f"✅ Dashboard stats: {data['total_products']} products, {data['orders_pending']} pending orders")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
