"""
Test Security Enhancement Features:
1. Staff password management (admin resets staff passwords)
2. Force password change on login
3. Admin security question for password recovery
4. Login page security (no admin credentials shown)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test Staff data
TEST_STAFF_EMAIL = f"test.staff.security.{int(time.time())}@example.com"
TEST_STAFF_PASSWORD = "testpass123"
TEST_STAFF_NAME = "TEST_Security_Staff"


class TestAuthEndpoints:
    """Test basic authentication and security endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin token for authenticated requests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        self.admin_token = data["token"]
        self.admin_id = data["user"]["id"]
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
    def test_admin_login_returns_force_password_change_flag(self):
        """Test that login response includes force_password_change flag"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check force_password_change is in response
        assert "force_password_change" in data, "force_password_change not in login response"
        assert "token" in data
        assert "user" in data
        assert "force_password_change" in data["user"], "force_password_change not in user object"
        print("✅ Login response includes force_password_change flag")
        
    def test_get_me_returns_has_security_question(self):
        """Test that /api/auth/me returns has_security_question flag"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        
        assert "has_security_question" in data, "has_security_question not in /auth/me response"
        print(f"✅ /auth/me returns has_security_question: {data['has_security_question']}")


class TestStaffPasswordManagement:
    """Test admin managing staff passwords"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session and create test staff"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        self.admin_token = data["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
        # Create test staff
        staff_email = f"test.staff.pwd.{int(time.time())}@example.com"
        response = self.session.post(f"{BASE_URL}/api/employees", json={
            "name": "TEST_Password_Staff",
            "email": staff_email,
            "password": "initialpass123",
            "role": "staff"
        })
        assert response.status_code == 200
        self.test_staff = response.json()
        self.test_staff_email = staff_email
        
        yield
        
        # Cleanup - delete test staff
        self.session.delete(f"{BASE_URL}/api/employees/{self.test_staff['id']}")
        
    def test_admin_reset_staff_password(self):
        """Test POST /api/employees/{id}/reset-password for staff"""
        response = self.session.post(
            f"{BASE_URL}/api/employees/{self.test_staff['id']}/reset-password",
            json={
                "new_password": "newpassword456",
                "force_change_on_login": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Password reset" in data["message"]
        print(f"✅ Admin reset staff password: {data['message']}")
        
        # Verify new password works
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_staff_email,
            "password": "newpassword456"
        })
        assert login_response.status_code == 200, "Staff cannot login with new password"
        print("✅ Staff can login with new password")
        
    def test_admin_reset_staff_password_with_force_change(self):
        """Test reset password with force_change_on_login=True"""
        response = self.session.post(
            f"{BASE_URL}/api/employees/{self.test_staff['id']}/reset-password",
            json={
                "new_password": "temppass789",
                "force_change_on_login": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("force_change_on_login") == True
        print("✅ Password reset with force_change_on_login=True")
        
        # Verify login returns force_password_change=True
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_staff_email,
            "password": "temppass789"
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["force_password_change"] == True, "force_password_change should be True after admin reset"
        print("✅ Login response shows force_password_change=True")
        
    def test_admin_cannot_reset_another_admin_password(self):
        """Test that admin cannot reset another admin's password via this endpoint"""
        # Create another admin
        admin_email = f"test.admin.{int(time.time())}@example.com"
        response = self.session.post(f"{BASE_URL}/api/employees", json={
            "name": "TEST_Another_Admin",
            "email": admin_email,
            "password": "adminpass123",
            "role": "admin"
        })
        assert response.status_code == 200
        other_admin = response.json()
        
        try:
            # Try to reset another admin's password
            reset_response = self.session.post(
                f"{BASE_URL}/api/employees/{other_admin['id']}/reset-password",
                json={
                    "new_password": "hackedpass",
                    "force_change_on_login": False
                }
            )
            assert reset_response.status_code == 403, f"Should not be able to reset another admin's password, got {reset_response.status_code}"
            print("✅ Admin cannot reset another admin's password")
        finally:
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/employees/{other_admin['id']}")
            
    def test_employees_list_shows_force_password_change(self):
        """Test that GET /api/employees shows force_password_change flag"""
        # First set force_change_on_login for test staff
        self.session.post(
            f"{BASE_URL}/api/employees/{self.test_staff['id']}/reset-password",
            json={
                "new_password": "temppass123",
                "force_change_on_login": True
            }
        )
        
        response = self.session.get(f"{BASE_URL}/api/employees")
        assert response.status_code == 200
        employees = response.json()
        
        # Find our test staff
        test_emp = next((e for e in employees if e["id"] == self.test_staff["id"]), None)
        assert test_emp is not None, "Test staff not found in employees list"
        assert "force_password_change" in test_emp, "force_password_change not in employee response"
        assert test_emp["force_password_change"] == True, "force_password_change should be True"
        print("✅ Employees list shows force_password_change flag")


class TestChangePassword:
    """Test user changing their own password"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session and create test staff"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin to create staff
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        admin_token = response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        # Create test staff
        self.staff_email = f"test.change.pwd.{int(time.time())}@example.com"
        response = self.session.post(f"{BASE_URL}/api/employees", json={
            "name": "TEST_ChangePassword_Staff",
            "email": self.staff_email,
            "password": "oldpass123",
            "role": "staff"
        })
        assert response.status_code == 200
        self.test_staff = response.json()
        
        yield
        
        # Cleanup
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json"})
        admin_login = admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        if admin_login.status_code == 200:
            admin_session.headers.update({"Authorization": f"Bearer {admin_login.json()['token']}"})
            admin_session.delete(f"{BASE_URL}/api/employees/{self.test_staff['id']}")
        
    def test_user_change_own_password(self):
        """Test POST /api/auth/change-password"""
        # Login as staff
        staff_session = requests.Session()
        staff_session.headers.update({"Content-Type": "application/json"})
        
        login_response = staff_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.staff_email,
            "password": "oldpass123"
        })
        assert login_response.status_code == 200
        staff_token = login_response.json()["token"]
        staff_session.headers.update({"Authorization": f"Bearer {staff_token}"})
        
        # Change password
        response = staff_session.post(f"{BASE_URL}/api/auth/change-password", json={
            "current_password": "oldpass123",
            "new_password": "newpass456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ User changed own password: {data['message']}")
        
        # Verify old password no longer works
        old_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.staff_email,
            "password": "oldpass123"
        })
        assert old_login.status_code == 401, "Old password should not work"
        print("✅ Old password no longer works")
        
        # Verify new password works
        new_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.staff_email,
            "password": "newpass456"
        })
        assert new_login.status_code == 200, "New password should work"
        print("✅ New password works")
        
    def test_change_password_wrong_current_password(self):
        """Test change password with wrong current password"""
        # Login as staff
        staff_session = requests.Session()
        staff_session.headers.update({"Content-Type": "application/json"})
        
        login_response = staff_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.staff_email,
            "password": "oldpass123"
        })
        assert login_response.status_code == 200
        staff_token = login_response.json()["token"]
        staff_session.headers.update({"Authorization": f"Bearer {staff_token}"})
        
        # Try to change with wrong current password
        response = staff_session.post(f"{BASE_URL}/api/auth/change-password", json={
            "current_password": "wrongpassword",
            "new_password": "newpass456"
        })
        assert response.status_code == 401, f"Should reject wrong current password, got {response.status_code}"
        print("✅ Change password rejects wrong current password")


class TestSecurityQuestion:
    """Test admin security question for password recovery"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        self.admin_token = response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
    def test_set_security_question(self):
        """Test POST /api/auth/set-security-question"""
        response = self.session.post(f"{BASE_URL}/api/auth/set-security-question", json={
            "security_question": "What was the name of your first pet?",
            "security_answer": "buddy",
            "current_password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Security question set: {data['message']}")
        
    def test_set_security_question_wrong_password(self):
        """Test setting security question with wrong password"""
        response = self.session.post(f"{BASE_URL}/api/auth/set-security-question", json={
            "security_question": "Test question",
            "security_answer": "test",
            "current_password": "wrongpassword"
        })
        assert response.status_code == 401, f"Should reject wrong password, got {response.status_code}"
        print("✅ Set security question rejects wrong password")
        
    def test_get_security_question_for_admin(self):
        """Test GET /api/auth/security-question/{email}"""
        response = requests.get(f"{BASE_URL}/api/auth/security-question/admin@sellandiamman.com")
        assert response.status_code == 200
        data = response.json()
        assert "security_question" in data
        print(f"✅ Got security question: {data['security_question']}")
        
    def test_get_security_question_for_non_admin(self):
        """Test that non-admin cannot use security question reset"""
        # First create a staff member
        response = self.session.post(f"{BASE_URL}/api/employees", json={
            "name": "TEST_Staff_NoSecQ",
            "email": f"test.nosecq.{int(time.time())}@example.com",
            "password": "staffpass123",
            "role": "staff"
        })
        assert response.status_code == 200
        staff = response.json()
        
        try:
            # Try to get security question for staff
            secq_response = requests.get(f"{BASE_URL}/api/auth/security-question/{staff['email']}")
            assert secq_response.status_code == 400, f"Should reject non-admin, got {secq_response.status_code}"
            print("✅ Security question endpoint rejects non-admin accounts")
        finally:
            self.session.delete(f"{BASE_URL}/api/employees/{staff['id']}")
            
    def test_reset_password_with_security_question(self):
        """Test POST /api/auth/reset-password-with-security"""
        # First ensure security question is set
        self.session.post(f"{BASE_URL}/api/auth/set-security-question", json={
            "security_question": "What was the name of your first pet?",
            "security_answer": "buddy",
            "current_password": "admin123"
        })
        
        # Reset password using security question
        response = requests.post(f"{BASE_URL}/api/auth/reset-password-with-security", json={
            "email": "admin@sellandiamman.com",
            "security_answer": "buddy",
            "new_password": "admin123"  # Reset back to original
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Password reset with security question: {data['message']}")
        
    def test_reset_password_wrong_answer(self):
        """Test reset password with wrong security answer"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password-with-security", json={
            "email": "admin@sellandiamman.com",
            "security_answer": "wronganswer",
            "new_password": "hackedpassword"
        })
        assert response.status_code == 401, f"Should reject wrong answer, got {response.status_code}"
        print("✅ Reset password rejects wrong security answer")
        
    def test_security_answer_case_insensitive(self):
        """Test that security answer is case-insensitive"""
        # Set security question with lowercase answer
        self.session.post(f"{BASE_URL}/api/auth/set-security-question", json={
            "security_question": "What was the name of your first pet?",
            "security_answer": "buddy",
            "current_password": "admin123"
        })
        
        # Reset with uppercase answer
        response = requests.post(f"{BASE_URL}/api/auth/reset-password-with-security", json={
            "email": "admin@sellandiamman.com",
            "security_answer": "BUDDY",
            "new_password": "admin123"
        })
        assert response.status_code == 200, f"Security answer should be case-insensitive, got {response.status_code}"
        print("✅ Security answer is case-insensitive")


class TestPasswordValidation:
    """Test password validation rules"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@sellandiamman.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        self.admin_token = response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
    def test_reset_password_min_length(self):
        """Test that password must be at least 6 characters"""
        # Create test staff
        response = self.session.post(f"{BASE_URL}/api/employees", json={
            "name": "TEST_MinLength_Staff",
            "email": f"test.minlen.{int(time.time())}@example.com",
            "password": "initialpass123",
            "role": "staff"
        })
        assert response.status_code == 200
        staff = response.json()
        
        try:
            # Try to reset with short password
            reset_response = self.session.post(
                f"{BASE_URL}/api/employees/{staff['id']}/reset-password",
                json={
                    "new_password": "short",  # Only 5 chars
                    "force_change_on_login": False
                }
            )
            assert reset_response.status_code == 422, f"Should reject short password, got {reset_response.status_code}"
            print("✅ Password minimum length validation works")
        finally:
            self.session.delete(f"{BASE_URL}/api/employees/{staff['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
