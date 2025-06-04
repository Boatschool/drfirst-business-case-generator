#!/usr/bin/env python3
"""
HITL Financial Estimates Testing Script
Tests the complete workflow for editing and submitting financial estimates for review.
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class HitlFinancialEstimatesTest:
    def __init__(self, base_url: str = "http://localhost:8000", auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json"
        }
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        
        self.test_case_id = None
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise

    def test_1_setup_test_case(self):
        """Create a test business case with financial estimates"""
        print("\n🔧 Setting up test case with financial estimates...")
        
        # First, create a business case
        case_data = {
            "request_type": "initiate_case",
            "payload": {
                "problemStatement": "Test case for HITL financial estimates - automated testing",
                "projectTitle": "HITL Financial Test Case",
                "relevantLinks": [{"name": "Test Link", "url": "https://example.com"}]
            }
        }
        
        response = self.make_request("POST", "/api/v1/agents/invoke", case_data)
        
        if response.status_code == 200:
            result = response.json()
            self.test_case_id = result.get("caseId")
            self.log_test("Create test business case", True, f"Case ID: {self.test_case_id}")
            
            # Wait for the case to process and generate estimates
            print("    Waiting for agents to generate estimates...")
            time.sleep(10)  # Give time for agents to work
            
            return True
        else:
            self.log_test("Create test business case", False, f"Status: {response.status_code}")
            return False

    def test_2_verify_initial_estimates(self):
        """Verify that financial estimates were created by agents"""
        print("\n🔍 Verifying initial financial estimates...")
        
        if not self.test_case_id:
            self.log_test("Verify initial estimates", False, "No test case ID")
            return False
        
        response = self.make_request("GET", f"/api/v1/cases/{self.test_case_id}")
        
        if response.status_code == 200:
            case_details = response.json()
            
            # Check for effort estimate
            has_effort = case_details.get("effort_estimate_v1") is not None
            self.log_test("Initial effort estimate exists", has_effort)
            
            # Check for cost estimate
            has_cost = case_details.get("cost_estimate_v1") is not None
            self.log_test("Initial cost estimate exists", has_cost)
            
            # Check for value projection
            has_value = case_details.get("value_projection_v1") is not None
            self.log_test("Initial value projection exists", has_value)
            
            # Store original estimates for comparison
            self.original_effort = case_details.get("effort_estimate_v1")
            self.original_cost = case_details.get("cost_estimate_v1")
            self.original_value = case_details.get("value_projection_v1")
            
            return has_effort and has_cost and has_value
        else:
            self.log_test("Verify initial estimates", False, f"Status: {response.status_code}")
            return False

    def test_3_update_effort_estimate(self):
        """Test updating effort estimate"""
        print("\n✏️ Testing effort estimate updates...")
        
        if not self.test_case_id or not self.original_effort:
            self.log_test("Update effort estimate", False, "Missing test case or original effort estimate")
            return False
        
        # Prepare updated effort estimate
        updated_effort = {
            "roles": [
                {"role": "Senior Developer", "hours": 120},
                {"role": "QA Engineer", "hours": 40},
                {"role": "DevOps Engineer", "hours": 20}
            ],
            "total_hours": 180,
            "estimated_duration_weeks": 6,
            "complexity_assessment": "Medium-High (Updated via HITL)",
            "notes": "Updated through HITL testing - modified estimates based on detailed analysis"
        }
        
        response = self.make_request("PUT", f"/api/v1/cases/{self.test_case_id}/effort-estimate", updated_effort)
        
        if response.status_code == 200:
            self.log_test("Update effort estimate", True, "Successfully updated effort estimate")
            return True
        else:
            self.log_test("Update effort estimate", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_4_submit_effort_estimate(self):
        """Test submitting effort estimate for review"""
        print("\n📤 Testing effort estimate submission...")
        
        if not self.test_case_id:
            self.log_test("Submit effort estimate", False, "No test case ID")
            return False
        
        response = self.make_request("POST", f"/api/v1/cases/{self.test_case_id}/effort-estimate/submit")
        
        if response.status_code == 200:
            result = response.json()
            new_status = result.get("new_status")
            expected_status = "EFFORT_PENDING_REVIEW"
            
            if new_status == expected_status:
                self.log_test("Submit effort estimate", True, f"Status changed to {new_status}")
                return True
            else:
                self.log_test("Submit effort estimate", False, f"Expected {expected_status}, got {new_status}")
                return False
        else:
            self.log_test("Submit effort estimate", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_5_update_cost_estimate(self):
        """Test updating cost estimate"""
        print("\n💰 Testing cost estimate updates...")
        
        if not self.test_case_id or not self.original_cost:
            self.log_test("Update cost estimate", False, "Missing test case or original cost estimate")
            return False
        
        # Prepare updated cost estimate
        updated_cost = {
            "estimated_cost": 45000.00,
            "currency": "USD",
            "rate_card_used": "Standard 2024 Rates (Updated)",
            "role_breakdown": [
                {
                    "role": "Senior Developer",
                    "hours": 120,
                    "hourly_rate": 150.00,
                    "total_cost": 18000.00,
                    "currency": "USD"
                },
                {
                    "role": "QA Engineer", 
                    "hours": 40,
                    "hourly_rate": 100.00,
                    "total_cost": 4000.00,
                    "currency": "USD"
                },
                {
                    "role": "DevOps Engineer",
                    "hours": 20,
                    "hourly_rate": 125.00,
                    "total_cost": 2500.00,
                    "currency": "USD"
                }
            ],
            "calculation_method": "Updated hourly rates based on 2024 market analysis",
            "notes": "Costs updated via HITL process - includes updated market rates and additional buffer"
        }
        
        response = self.make_request("PUT", f"/api/v1/cases/{self.test_case_id}/cost-estimate", updated_cost)
        
        if response.status_code == 200:
            self.log_test("Update cost estimate", True, "Successfully updated cost estimate")
            return True
        else:
            self.log_test("Update cost estimate", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_6_submit_cost_estimate(self):
        """Test submitting cost estimate for review"""
        print("\n📤 Testing cost estimate submission...")
        
        if not self.test_case_id:
            self.log_test("Submit cost estimate", False, "No test case ID")
            return False
        
        response = self.make_request("POST", f"/api/v1/cases/{self.test_case_id}/cost-estimate/submit")
        
        if response.status_code == 200:
            result = response.json()
            new_status = result.get("new_status")
            expected_status = "COSTING_PENDING_REVIEW"
            
            if new_status == expected_status:
                self.log_test("Submit cost estimate", True, f"Status changed to {new_status}")
                return True
            else:
                self.log_test("Submit cost estimate", False, f"Expected {expected_status}, got {new_status}")
                return False
        else:
            self.log_test("Submit cost estimate", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_7_update_value_projection(self):
        """Test updating value projection"""
        print("\n📈 Testing value projection updates...")
        
        if not self.test_case_id or not self.original_value:
            self.log_test("Update value projection", False, "Missing test case or original value projection")
            return False
        
        # Prepare updated value projection
        updated_value = {
            "scenarios": [
                {
                    "case": "Conservative",
                    "value": 150000,
                    "description": "Conservative estimate with minimal adoption"
                },
                {
                    "case": "Base",
                    "value": 300000,
                    "description": "Expected value with normal adoption rate"
                },
                {
                    "case": "Optimistic",
                    "value": 500000,
                    "description": "High adoption with additional market opportunities"
                }
            ],
            "currency": "USD",
            "template_used": "Updated SaaS Revenue Template 2024",
            "methodology": "Updated DCF analysis with market research",
            "assumptions": [
                "Updated market penetration rates based on 2024 data",
                "Revised customer acquisition costs",
                "Enhanced feature adoption rates",
                "Updated competitive landscape analysis"
            ],
            "notes": "Value projection updated via HITL process - incorporates latest market research and competitive analysis"
        }
        
        response = self.make_request("PUT", f"/api/v1/cases/{self.test_case_id}/value-projection", updated_value)
        
        if response.status_code == 200:
            self.log_test("Update value projection", True, "Successfully updated value projection")
            return True
        else:
            self.log_test("Update value projection", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_8_submit_value_projection(self):
        """Test submitting value projection for review"""
        print("\n📤 Testing value projection submission...")
        
        if not self.test_case_id:
            self.log_test("Submit value projection", False, "No test case ID")
            return False
        
        response = self.make_request("POST", f"/api/v1/cases/{self.test_case_id}/value-projection/submit")
        
        if response.status_code == 200:
            result = response.json()
            new_status = result.get("new_status")
            expected_status = "VALUE_PENDING_REVIEW"
            
            if new_status == expected_status:
                self.log_test("Submit value projection", True, f"Status changed to {new_status}")
                return True
            else:
                self.log_test("Submit value projection", False, f"Expected {expected_status}, got {new_status}")
                return False
        else:
            self.log_test("Submit value projection", False, f"Status: {response.status_code}, Response: {response.text}")
            return False

    def test_9_verify_final_state(self):
        """Verify final case state and history"""
        print("\n🔍 Verifying final case state...")
        
        if not self.test_case_id:
            self.log_test("Verify final state", False, "No test case ID")
            return False
        
        response = self.make_request("GET", f"/api/v1/cases/{self.test_case_id}")
        
        if response.status_code == 200:
            case_details = response.json()
            
            # Check that estimates were updated
            current_effort = case_details.get("effort_estimate_v1")
            current_cost = case_details.get("cost_estimate_v1")
            current_value = case_details.get("value_projection_v1")
            
            # Verify effort estimate changes
            effort_updated = (current_effort.get("notes", "") != self.original_effort.get("notes", ""))
            self.log_test("Effort estimate was updated", effort_updated)
            
            # Verify cost estimate changes  
            cost_updated = (current_cost.get("notes", "") != self.original_cost.get("notes", ""))
            self.log_test("Cost estimate was updated", cost_updated)
            
            # Verify value projection changes
            value_updated = (current_value.get("notes", "") != self.original_value.get("notes", ""))
            self.log_test("Value projection was updated", value_updated)
            
            # Check history for HITL entries
            history = case_details.get("history", [])
            hitl_entries = [entry for entry in history if "ESTIMATE" in entry.get("messageType", "")]
            
            has_effort_history = any("EFFORT" in entry.get("messageType", "") for entry in hitl_entries)
            has_cost_history = any("COST" in entry.get("messageType", "") for entry in hitl_entries)
            has_value_history = any("VALUE" in entry.get("messageType", "") for entry in hitl_entries)
            
            self.log_test("Effort estimate history logged", has_effort_history)
            self.log_test("Cost estimate history logged", has_cost_history)
            self.log_test("Value projection history logged", has_value_history)
            
            return all([effort_updated, cost_updated, value_updated, has_effort_history, has_cost_history, has_value_history])
        else:
            self.log_test("Verify final state", False, f"Status: {response.status_code}")
            return False

    def test_10_authorization_checks(self):
        """Test authorization and status validation"""
        print("\n🔒 Testing authorization and status validation...")
        
        # Test without authentication
        original_headers = self.headers.copy()
        self.headers = {"Content-Type": "application/json"}  # Remove auth header
        
        response = self.make_request("PUT", f"/api/v1/cases/{self.test_case_id}/effort-estimate", {
            "roles": [{"role": "Test", "hours": 1}],
            "total_hours": 1,
            "estimated_duration_weeks": 1,
            "complexity_assessment": "Test"
        })
        
        unauthorized_blocked = response.status_code == 401
        self.log_test("Unauthorized access blocked", unauthorized_blocked)
        
        # Restore headers
        self.headers = original_headers
        
        return unauthorized_blocked

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting HITL Financial Estimates Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_1_setup_test_case,
            self.test_2_verify_initial_estimates,
            self.test_3_update_effort_estimate,
            self.test_4_submit_effort_estimate,
            self.test_5_update_cost_estimate,
            self.test_6_submit_cost_estimate,
            self.test_7_update_value_projection,
            self.test_8_submit_value_projection,
            self.test_9_verify_final_state,
            self.test_10_authorization_checks
        ]
        
        passed = 0
        total = 0
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                total += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if self.test_case_id:
            print(f"🔗 Test case created: {self.test_case_id}")
            print(f"   View at: {self.base_url}/cases/{self.test_case_id}")
        
        # Save detailed results
        with open("hitl_financial_estimates_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "total": total,
                    "success_rate": passed / total if total > 0 else 0,
                    "test_case_id": self.test_case_id,
                    "timestamp": datetime.now().isoformat()
                },
                "details": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: hitl_financial_estimates_test_results.json")
        
        return passed == total


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test HITL Financial Estimates functionality")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--auth-token", help="Authentication token (if required)")
    
    args = parser.parse_args()
    
    tester = HitlFinancialEstimatesTest(args.base_url, args.auth_token)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! HITL Financial Estimates functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 