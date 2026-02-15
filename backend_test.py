#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class SellandiammanTradersAPITester:
    def __init__(self, base_url="https://sellandia-inventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.staff_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_products = []
        self.created_orders = []
        self.created_staff = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response": response_data if response_data else {}
        })

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_token: str = None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        
        if use_token:
            token = self.admin_token if use_token == 'admin' else self.staff_token
            if token:
                test_headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            response_data = {}
            try:
                response_data = response.json()
            except:
                response_data = {"raw": response.text[:200]}

            self.log_test(
                name, 
                success, 
                f"Expected {expected_status}, got {response.status_code}" if not success else "",
                response_data
            )
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_auth_flow(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@sellandiamman.com", "password": "admin123"}
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"  📝 Admin token acquired: {self.admin_token[:20]}...")
        else:
            print("  ❌ Failed to get admin token - stopping tests")
            return False
        
        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST", 
            "auth/login",
            401,
            data={"email": "wrong@email.com", "password": "wrong"}
        )
        
        # Test /me endpoint
        self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200,
            use_token='admin'
        )
        
        return True

    def test_staff_management(self):
        """Test staff management endpoints"""
        print("\n👥 Testing Staff Management...")
        
        # Create a test staff member
        staff_data = {
            "name": "Test Staff",
            "email": f"teststaff_{int(datetime.now().timestamp())}@sellandiamman.com",
            "role": "staff",
            "password": "testpass123"
        }
        
        success, response = self.run_test(
            "Create Staff Member",
            "POST",
            "employees",
            200,
            data=staff_data,
            use_token='admin'
        )
        
        if success:
            self.created_staff.append(response)
            
            # Test staff login
            staff_login_success, staff_response = self.run_test(
                "Staff Login",
                "POST",
                "auth/login", 
                200,
                data={"email": staff_data["email"], "password": staff_data["password"]}
            )
            
            if staff_login_success:
                self.staff_token = staff_response['token']
                print(f"  📝 Staff token acquired: {self.staff_token[:20]}...")
        
        # List employees
        self.run_test(
            "List Employees",
            "GET",
            "employees",
            200,
            use_token='admin'
        )

    def test_product_management(self):
        """Test product management endpoints"""
        print("\n📦 Testing Product Management...")
        
        # Test product creation with location code
        product_data = {
            "sku": f"TEST{int(datetime.now().timestamp())}",
            "product_name": "Test Wire Cable",
            "category": "Wires & Cables",
            "brand": "Test Brand",
            "zone": "A",
            "aisle": 5,
            "rack": 10,
            "shelf": 2,
            "bin": 15,
            "quantity_available": 100,
            "reorder_level": 10,
            "supplier": "Test Supplier",
            "image_url": "https://example.com/image.jpg"
        }
        
        success, response = self.run_test(
            "Create Product",
            "POST",
            "products",
            200,
            data=product_data,
            use_token='admin'
        )
        
        if success:
            self.created_products.append(response)
            expected_location = "A-05-R10-S2-B15"
            actual_location = response.get('full_location_code', '')
            
            if actual_location == expected_location:
                self.log_test(
                    "Location Code Generation", 
                    True, 
                    f"Generated: {actual_location}"
                )
            else:
                self.log_test(
                    "Location Code Generation", 
                    False, 
                    f"Expected: {expected_location}, Got: {actual_location}"
                )
        
        # Test product search (staff access)
        self.run_test(
            "Search Products (Staff)",
            "GET",
            "products?search=Test",
            200,
            use_token='staff' if self.staff_token else 'admin'
        )
        
        # Test categories endpoint
        self.run_test(
            "Get Categories",
            "GET",
            "products/categories",
            200,
            use_token='admin'
        )
        
        # Test zones endpoint
        self.run_test(
            "Get Zones",
            "GET",
            "products/zones",
            200,
            use_token='admin'
        )

    def test_public_endpoints(self):
        """Test public endpoints (no auth required)"""
        print("\n🌐 Testing Public Endpoints...")
        
        # Test public catalogue (should not show stock)
        success, response = self.run_test(
            "Public Catalogue",
            "GET",
            "public/catalogue",
            200
        )
        
        if success and response:
            # Check that stock information is not included
            products = response if isinstance(response, list) else []
            stock_fields_found = []
            
            for product in products[:3]:  # Check first 3 products
                for field in ['quantity_available', 'reorder_level', 'full_location_code']:
                    if field in product:
                        stock_fields_found.append(field)
            
            if stock_fields_found:
                self.log_test(
                    "Public Catalogue Stock Privacy",
                    False,
                    f"Found restricted fields: {stock_fields_found}"
                )
            else:
                self.log_test(
                    "Public Catalogue Stock Privacy",
                    True,
                    "No stock information exposed"
                )
        
        # Test public categories
        self.run_test(
            "Public Categories",
            "GET",
            "public/categories",
            200
        )

    def test_order_workflow(self):
        """Test complete order and picking workflow"""
        print("\n📋 Testing Order & Picking Workflow...")
        
        if not self.created_products:
            print("  ⚠️  No products available for order testing")
            return
        
        product = self.created_products[0]
        
        # Create order
        order_data = {
            "customer_name": "Test Customer",
            "items": [
                {
                    "sku": product["sku"],
                    "quantity_required": 5
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Order",
            "POST",
            "orders",
            200,
            data=order_data,
            use_token='staff' if self.staff_token else 'admin'
        )
        
        if success:
            order = response
            self.created_orders.append(order)
            
            # Verify order number format (ORD-YYYYMMDD-XXXX)
            order_number = order.get('order_number', '')
            today = datetime.now().strftime("%Y%m%d")
            expected_prefix = f"ORD-{today}-"
            
            if order_number.startswith(expected_prefix):
                self.log_test(
                    "Order Number Format",
                    True,
                    f"Generated: {order_number}"
                )
            else:
                self.log_test(
                    "Order Number Format", 
                    False,
                    f"Expected prefix: {expected_prefix}, Got: {order_number}"
                )
            
            # Get order details
            self.run_test(
                "Get Order Details",
                "GET", 
                f"orders/{order['id']}",
                200,
                use_token='admin'
            )
            
            # Test picking workflow - mark item as picked
            if order.get('items') and len(order['items']) > 0:
                item_id = order['items'][0]['id']
                original_stock = product['quantity_available']
                
                success, pick_response = self.run_test(
                    "Mark Item as Picked",
                    "PATCH",
                    f"orders/{order['id']}/items/{item_id}/pick",
                    200,
                    use_token='admin'
                )
                
                if success:
                    # Verify stock deduction
                    success, updated_product = self.run_test(
                        "Get Updated Product (Stock Check)",
                        "GET",
                        f"products/{product['id']}",
                        200,
                        use_token='admin'
                    )
                    
                    if success:
                        new_stock = updated_product.get('quantity_available', original_stock)
                        expected_stock = original_stock - 5  # quantity_required
                        
                        if new_stock == expected_stock:
                            self.log_test(
                                "Auto Stock Deduction",
                                True,
                                f"Stock: {original_stock} → {new_stock}"
                            )
                        else:
                            self.log_test(
                                "Auto Stock Deduction",
                                False,
                                f"Expected: {expected_stock}, Got: {new_stock}"
                            )

    def test_dashboard_endpoints(self):
        """Test dashboard and analytics endpoints"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        # Test dashboard stats
        self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200,
            use_token='admin'
        )
        
        # Test zone distribution
        self.run_test(
            "Zone Distribution",
            "GET", 
            "dashboard/zone-distribution",
            200,
            use_token='admin'
        )
        
        # Test category distribution  
        self.run_test(
            "Category Distribution",
            "GET",
            "dashboard/category-distribution", 
            200,
            use_token='admin'
        )
        
        # Test recent transactions
        self.run_test(
            "Recent Transactions",
            "GET",
            "dashboard/recent-transactions",
            200,
            use_token='admin'
        )
        
        # Test low stock items
        self.run_test(
            "Low Stock Items", 
            "GET",
            "dashboard/low-stock-items",
            200,
            use_token='admin'
        )

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        
        self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )

    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test orders
        for order in self.created_orders:
            self.run_test(
                f"Delete Order {order['order_number']}",
                "DELETE",
                f"orders/{order['id']}",
                200,
                use_token='admin'
            )
        
        # Delete test products  
        for product in self.created_products:
            self.run_test(
                f"Delete Product {product['sku']}",
                "DELETE", 
                f"products/{product['id']}",
                200,
                use_token='admin'
            )
        
        # Delete test staff
        for staff in self.created_staff:
            self.run_test(
                f"Delete Staff {staff['email']}",
                "DELETE",
                f"employees/{staff['id']}",
                200,
                use_token='admin'
            )

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Sellandiamman Traders API Tests")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        try:
            # Test authentication first
            if not self.test_auth_flow():
                print("\n❌ Authentication failed - stopping tests")
                return False
            
            # Run all test suites
            self.test_health_endpoints()
            self.test_staff_management()  
            self.test_product_management()
            self.test_public_endpoints()
            self.test_order_workflow()
            self.test_dashboard_endpoints()
            
            # Cleanup
            self.cleanup()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if not t['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = SellandiammanTradersAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())