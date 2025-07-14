#!/usr/bin/env python3
"""
Backend API Tests for Lacs Verts Application
Tests all backend endpoints according to the review request priorities
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://1321b751-1671-4576-bd62-76dfa0610534.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_api_root(self):
        """Test GET /api/ - Basic API test"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Lacs Verts API" in data["message"]:
                    self.log_result("API Root", True, "API root endpoint working correctly")
                    return True
                else:
                    self.log_result("API Root", False, "Unexpected response format", data)
                    return False
            else:
                self.log_result("API Root", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("API Root", False, "Connection error", str(e))
            return False
    
    def test_lakes_endpoint(self):
        """Test GET /api/lakes - Retrieve lakes from Côte d'Ivoire"""
        try:
            response = self.session.get(f"{BACKEND_URL}/lakes")
            
            if response.status_code == 200:
                lakes = response.json()
                
                if not isinstance(lakes, list):
                    self.log_result("Lakes Endpoint", False, "Response is not a list", type(lakes))
                    return False
                
                if len(lakes) == 0:
                    self.log_result("Lakes Endpoint", False, "No sample lakes found - initialization may have failed")
                    return False
                
                # Verify sample data structure
                expected_lakes = ["Lac de Kossou", "Lac Buyo", "Lac de Taabo", "Lac de Ayamé"]
                found_lakes = [lake.get("name") for lake in lakes]
                
                missing_lakes = [name for name in expected_lakes if name not in found_lakes]
                if missing_lakes:
                    self.log_result("Lakes Endpoint", False, f"Missing expected lakes: {missing_lakes}", found_lakes)
                    return False
                
                # Verify lake data structure
                for lake in lakes:
                    required_fields = ["id", "name", "latitude", "longitude", "status", "region"]
                    missing_fields = [field for field in required_fields if field not in lake]
                    if missing_fields:
                        self.log_result("Lakes Endpoint", False, f"Lake missing required fields: {missing_fields}", lake)
                        return False
                    
                    # Verify status values
                    if lake["status"] not in ["propre", "à surveiller", "pollué"]:
                        self.log_result("Lakes Endpoint", False, f"Invalid lake status: {lake['status']}", lake)
                        return False
                
                self.log_result("Lakes Endpoint", True, f"Successfully retrieved {len(lakes)} lakes with correct structure")
                return True
                
            else:
                self.log_result("Lakes Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Lakes Endpoint", False, "Connection error", str(e))
            return False
    
    def test_awareness_endpoint(self):
        """Test GET /api/awareness - Retrieve awareness posts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/awareness")
            
            if response.status_code == 200:
                posts = response.json()
                
                if not isinstance(posts, list):
                    self.log_result("Awareness Endpoint", False, "Response is not a list", type(posts))
                    return False
                
                # It's OK if there are no posts initially
                if len(posts) == 0:
                    self.log_result("Awareness Endpoint", True, "No awareness posts found (expected for new installation)")
                    return True
                
                # If posts exist, verify structure
                for post in posts:
                    required_fields = ["id", "title", "content", "author_id", "author_name", "created_at", "is_published"]
                    missing_fields = [field for field in required_fields if field not in post]
                    if missing_fields:
                        self.log_result("Awareness Endpoint", False, f"Post missing required fields: {missing_fields}", post)
                        return False
                
                self.log_result("Awareness Endpoint", True, f"Successfully retrieved {len(posts)} awareness posts")
                return True
                
            else:
                self.log_result("Awareness Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Awareness Endpoint", False, "Connection error", str(e))
            return False
    
    def test_auth_without_session(self):
        """Test POST /api/auth/profile - Should return 401 without session"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/profile")
            
            if response.status_code == 400:
                # Expected: Session ID required
                data = response.json()
                if "Session ID required" in data.get("detail", ""):
                    self.log_result("Auth Without Session", True, "Correctly returns 400 when no session ID provided")
                    return True
                else:
                    self.log_result("Auth Without Session", False, "Unexpected error message", data)
                    return False
            else:
                self.log_result("Auth Without Session", False, f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Auth Without Session", False, "Connection error", str(e))
            return False
    
    def test_auth_with_invalid_session(self):
        """Test POST /api/auth/profile - Should return 401 with invalid session"""
        try:
            headers = {"X-Session-ID": "invalid-session-token-12345"}
            response = self.session.post(f"{BACKEND_URL}/auth/profile", headers=headers)
            
            if response.status_code == 401:
                # Expected: Invalid session
                self.log_result("Auth Invalid Session", True, "Correctly returns 401 for invalid session")
                return True
            else:
                self.log_result("Auth Invalid Session", False, f"Expected 401, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Auth Invalid Session", False, "Connection error", str(e))
            return False
    
    def test_protected_endpoints_without_auth(self):
        """Test that protected endpoints return 401 without authentication"""
        protected_endpoints = [
            ("POST", "/reports", {"lake_id": "test", "description": "test"}),
            ("GET", "/reports", None),
            ("PUT", "/lakes/test-id/status", None),
            ("POST", "/awareness", {"title": "test", "content": "test"}),
            ("DELETE", "/awareness/test-id", None)
        ]
        
        all_passed = True
        
        for method, endpoint, data in protected_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json=data)
                elif method == "PUT":
                    response = self.session.put(f"{BACKEND_URL}{endpoint}", json={"status": "propre"})
                elif method == "DELETE":
                    response = self.session.delete(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 401:
                    self.log_result(f"Protected {method} {endpoint}", True, "Correctly requires authentication")
                else:
                    self.log_result(f"Protected {method} {endpoint}", False, f"Expected 401, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Protected {method} {endpoint}", False, "Connection error", str(e))
                all_passed = False
        
        return all_passed
    
    def test_individual_lake_endpoint(self):
        """Test GET /api/lakes/{lake_id} - Get individual lake"""
        try:
            # First get all lakes to get a valid ID
            lakes_response = self.session.get(f"{BACKEND_URL}/lakes")
            if lakes_response.status_code != 200:
                self.log_result("Individual Lake", False, "Could not get lakes list for testing")
                return False
            
            lakes = lakes_response.json()
            if not lakes:
                self.log_result("Individual Lake", False, "No lakes available for testing")
                return False
            
            # Test with first lake
            lake_id = lakes[0]["id"]
            response = self.session.get(f"{BACKEND_URL}/lakes/{lake_id}")
            
            if response.status_code == 200:
                lake = response.json()
                if lake["id"] == lake_id:
                    self.log_result("Individual Lake", True, f"Successfully retrieved lake: {lake['name']}")
                    return True
                else:
                    self.log_result("Individual Lake", False, "Lake ID mismatch", lake)
                    return False
            else:
                self.log_result("Individual Lake", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Individual Lake", False, "Connection error", str(e))
            return False
    
    def test_reports_by_lake_endpoint(self):
        """Test GET /api/reports/lake/{lake_id} - Public endpoint for lake reports"""
        try:
            # First get all lakes to get a valid ID
            lakes_response = self.session.get(f"{BACKEND_URL}/lakes")
            if lakes_response.status_code != 200:
                self.log_result("Reports by Lake", False, "Could not get lakes list for testing")
                return False
            
            lakes = lakes_response.json()
            if not lakes:
                self.log_result("Reports by Lake", False, "No lakes available for testing")
                return False
            
            # Test with first lake
            lake_id = lakes[0]["id"]
            response = self.session.get(f"{BACKEND_URL}/reports/lake/{lake_id}")
            
            if response.status_code == 200:
                reports = response.json()
                if isinstance(reports, list):
                    self.log_result("Reports by Lake", True, f"Successfully retrieved {len(reports)} reports for lake")
                    return True
                else:
                    self.log_result("Reports by Lake", False, "Response is not a list", type(reports))
                    return False
            else:
                self.log_result("Reports by Lake", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Reports by Lake", False, "Connection error", str(e))
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("BACKEND API TESTS FOR LACS VERTS APPLICATION")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print()
        
        # Priority tests from review request
        tests = [
            ("API Root Test", self.test_api_root),
            ("Lakes Endpoint Test", self.test_lakes_endpoint),
            ("Awareness Endpoint Test", self.test_awareness_endpoint),
            ("Auth Without Session Test", self.test_auth_without_session),
            ("Auth Invalid Session Test", self.test_auth_with_invalid_session),
            ("Protected Endpoints Test", self.test_protected_endpoints_without_auth),
            ("Individual Lake Test", self.test_individual_lake_endpoint),
            ("Reports by Lake Test", self.test_reports_by_lake_endpoint)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Print detailed results
        print("\nDETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']} {result['test']}: {result['message']}")
            if result['details'] and "FAIL" in result['status']:
                print(f"   Details: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)