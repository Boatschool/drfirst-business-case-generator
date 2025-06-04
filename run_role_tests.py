#!/usr/bin/env python3
"""
Comprehensive Test Runner for Role-Based Access Control System
Runs unit tests, integration tests, and E2E tests for the role system

Usage: python run_role_tests.py [--unit] [--integration] [--e2e] [--all]
"""

import subprocess
import sys
import os
import argparse
import asyncio
from datetime import datetime

class RoleTestRunner:
    """Test runner for role-based access control tests"""
    
    def __init__(self):
        self.test_results = {
            "unit": None,
            "integration": None, 
            "e2e": None
        }
        self.start_time = datetime.now()
    
    def run_unit_tests(self):
        """Run unit tests for role system"""
        print("🧪 Running Unit Tests...")
        print("-" * 40)
        
        try:
            # Run role-specific unit tests from backend directory
            cmd = [
                sys.executable, "-m", "pytest", 
                "tests/unit/test_user_roles.py",
                "-v", "--tb=short"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="backend")
            
            if result.returncode == 0:
                print("✅ Unit tests PASSED")
                self.test_results["unit"] = "PASSED"
            else:
                print("❌ Unit tests FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.test_results["unit"] = "FAILED"
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running unit tests: {e}")
            self.test_results["unit"] = "ERROR"
            return False
    
    def run_integration_tests(self):
        """Run integration tests for role system"""
        print("\n🔗 Running Integration Tests...")
        print("-" * 40)
        
        try:
            # Run role assignment integration tests from backend directory
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/integration/test_role_assignment.py",
                "-v", "--tb=short"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="backend")
            
            if result.returncode == 0:
                print("✅ Integration tests PASSED")
                self.test_results["integration"] = "PASSED"
            else:
                print("❌ Integration tests FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.test_results["integration"] = "FAILED"
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running integration tests: {e}")
            self.test_results["integration"] = "ERROR"
            return False
    
    async def run_e2e_tests(self):
        """Run end-to-end tests for role system"""
        print("\n🌐 Running End-to-End Tests...")
        print("-" * 40)
        
        try:
            # Check if backend and frontend are running
            if not self._check_services_running():
                print("⚠️  Warning: Backend or frontend services may not be running")
                print("   For full E2E testing, ensure both services are running:")
                print("   - Backend: cd backend && uvicorn app.main:app --reload --port 8000")
                print("   - Frontend: cd frontend && npm start")
            
            # Run E2E tests
            cmd = [sys.executable, "test_role_based_e2e.py"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("✅ E2E tests PASSED")
                self.test_results["e2e"] = "PASSED"
            else:
                print("❌ E2E tests FAILED")
                if stdout:
                    print("STDOUT:", stdout.decode())
                if stderr:
                    print("STDERR:", stderr.decode())
                self.test_results["e2e"] = "FAILED"
            
            return process.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running E2E tests: {e}")
            self.test_results["e2e"] = "ERROR"
            return False
    
    def run_role_script_tests(self):
        """Test role assignment scripts functionality"""
        print("\n📜 Testing Role Assignment Scripts...")
        print("-" * 40)
        
        scripts_to_test = [
            "scripts/set_user_role.py",
            "scripts/set_admin_role.py", 
            "scripts/set_developer_role.py",
            "scripts/set_sales_manager_role.py",
            "scripts/set_finance_approver_role.py",
            "scripts/set_product_owner_role.py"
        ]
        
        all_passed = True
        
        for script in scripts_to_test:
            if os.path.exists(script):
                print(f"  ✅ {script} exists")
                
                # Test script can show usage
                try:
                    result = subprocess.run(
                        [sys.executable, script], 
                        capture_output=True, 
                        text=True,
                        timeout=10
                    )
                    # Scripts should exit with code 1 when no args provided (showing usage)
                    if result.returncode == 1 and ("Usage:" in result.stdout or "usage:" in result.stdout.lower()):
                        print(f"  ✅ {script} shows proper usage")
                    else:
                        print(f"  ⚠️  {script} may have usage issues")
                        
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️  {script} timed out")
                except Exception as e:
                    print(f"  ❌ Error testing {script}: {e}")
                    all_passed = False
            else:
                print(f"  ❌ {script} not found")
                all_passed = False
        
        return all_passed
    
    def _check_services_running(self):
        """Check if backend and frontend services are running"""
        try:
            import requests
            
            # Check backend
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                backend_running = response.status_code == 200
            except:
                backend_running = False
            
            # Check frontend (simple check)
            try:
                response = requests.get("http://localhost:4000", timeout=2)
                frontend_running = response.status_code == 200
            except:
                frontend_running = False
            
            return backend_running and frontend_running
            
        except ImportError:
            print("  ⚠️  requests not available for service checking")
            return False
    
    def generate_summary_report(self):
        """Generate final test summary report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "="*60)
        print("🎯 ROLE SYSTEM TEST SUMMARY REPORT")
        print("="*60)
        
        print(f"📅 Test Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
        
        print("\n📊 Test Results:")
        
        total_tests = 0
        passed_tests = 0
        
        for test_type, result in self.test_results.items():
            if result is not None:
                total_tests += 1
                status_emoji = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⚠️"
                print(f"  {status_emoji} {test_type.title()} Tests: {result}")
                if result == "PASSED":
                    passed_tests += 1
        
        print(f"\n🏆 Overall: {passed_tests}/{total_tests} test suites passed")
        
        if passed_tests == total_tests and total_tests > 0:
            print("🎉 ALL ROLE TESTS PASSED! The role system is ready for production.")
        elif passed_tests > 0:
            print("⚠️  Some tests passed, but review failed tests before deployment.")
        else:
            print("❌ No tests passed. Role system needs review before deployment.")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if self.test_results.get("unit") == "PASSED":
            print("  ✅ Role enum and validation logic is solid")
        if self.test_results.get("integration") == "PASSED":
            print("  ✅ Role assignment and Firebase integration working")
        if self.test_results.get("e2e") == "PASSED":
            print("  ✅ End-to-end role workflows functioning correctly")
        
        if "FAILED" in self.test_results.values():
            print("  🔧 Fix failing tests before production deployment")
        if "ERROR" in self.test_results.values():
            print("  🔧 Resolve test environment issues")


async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="Run role system tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--scripts", action="store_true", help="Test role scripts only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # If no specific test type specified, run all
    if not any([args.unit, args.integration, args.e2e, args.scripts]):
        args.all = True
    
    print("🚀 DrFirst Business Case Generator - Role System Test Runner")
    print("="*65)
    
    runner = RoleTestRunner()
    
    try:
        if args.all or args.unit:
            runner.run_unit_tests()
        
        if args.all or args.integration:
            runner.run_integration_tests()
        
        if args.all or args.scripts:
            runner.run_role_script_tests()
        
        if args.all or args.e2e:
            await runner.run_e2e_tests()
        
        # Generate final report
        runner.generate_summary_report()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
    
    # Return appropriate exit code
    if all(result == "PASSED" for result in runner.test_results.values() if result is not None):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 