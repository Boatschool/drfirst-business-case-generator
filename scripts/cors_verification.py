#!/usr/bin/env python3
"""
CORS Configuration Verification Script for DrFirst Business Case Generator

This script verifies that the CORS configuration on deployed backends
correctly allows requests from authorized origins and blocks unauthorized ones.

Usage:
    python scripts/cors_verification.py --backend-url https://your-backend.run.app --frontend-url https://your-frontend.web.app
    python scripts/cors_verification.py --local  # Test local development setup
"""

import argparse
import json
import logging
import requests
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CorsVerifier:
    """Verifies CORS configuration for DrFirst Business Case Generator"""
    
    def __init__(self, backend_url: str, authorized_origins: List[str]):
        self.backend_url = backend_url.rstrip('/')
        self.authorized_origins = authorized_origins
        self.test_results = []
        
    def verify_cors_configuration(self) -> Dict:
        """
        Run comprehensive CORS verification tests
        
        Returns:
            Dict with test results and summary
        """
        logger.info("=" * 60)
        logger.info("🔍 Starting CORS Configuration Verification")
        logger.info(f"🔗 Backend URL: {self.backend_url}")
        logger.info(f"✅ Authorized Origins: {', '.join(self.authorized_origins)}")
        logger.info("=" * 60)
        
        results = {
            'backend_url': self.backend_url,
            'authorized_origins': self.authorized_origins,
            'tests': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        # Test 1: Check backend health endpoint
        health_result = self._test_backend_health()
        results['tests'].append(health_result)
        self._update_summary(results['summary'], health_result)
        
        # Test 2: Verify configured CORS origins from backend
        cors_config_result = self._test_cors_configuration()
        results['tests'].append(cors_config_result)
        self._update_summary(results['summary'], cors_config_result)
        
        # Test 3: Test authorized origins
        for origin in self.authorized_origins:
            test_result = self._test_authorized_origin(origin)
            results['tests'].append(test_result)
            self._update_summary(results['summary'], test_result)
        
        # Test 4: Test unauthorized origins
        unauthorized_origins = [
            'https://unauthorized-domain.com',
            'http://malicious-site.example.com',
            'https://attacker.com',
            'http://localhost:5000',  # Different port
            'http://127.0.0.1:5001'   # Different port
        ]
        
        for origin in unauthorized_origins:
            test_result = self._test_unauthorized_origin(origin)
            results['tests'].append(test_result)
            self._update_summary(results['summary'], test_result)
        
        # Generate summary report
        self._print_summary_report(results)
        
        return results
    
    def _test_backend_health(self) -> Dict:
        """Test if the backend is accessible and healthy"""
        logger.info("🏥 Testing backend health endpoint...")
        
        test_result = {
            'test_name': 'Backend Health Check',
            'test_type': 'health',
            'status': 'unknown',
            'details': {},
            'recommendations': []
        }
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            test_result['details'] = {
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'headers': dict(response.headers)
            }
            
            if response.status_code == 200:
                logger.info("✅ Backend health check passed")
                test_result['status'] = 'passed'
            else:
                logger.warning(f"⚠️  Backend returned status {response.status_code}")
                test_result['status'] = 'warning'
                test_result['recommendations'].append(
                    f"Backend returned status {response.status_code}, expected 200"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Backend health check failed: {e}")
            test_result['status'] = 'failed'
            test_result['details']['error'] = str(e)
            test_result['recommendations'].append(
                "Backend is not accessible. Check deployment status and URL."
            )
        
        return test_result
    
    def _test_cors_configuration(self) -> Dict:
        """Test what CORS origins are actually configured on the backend"""
        logger.info("⚙️  Checking backend CORS configuration...")
        
        test_result = {
            'test_name': 'Backend CORS Configuration',
            'test_type': 'cors_config',
            'status': 'unknown',
            'details': {},
            'recommendations': []
        }
        
        try:
            # Try to get CORS info from a diagnostic endpoint if available
            response = requests.get(f"{self.backend_url}/api/v1/diagnostics/status", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    cors_config = data.get('configuration', {}).get('cors_origins', [])
                    
                    test_result['details'] = {
                        'configured_origins': cors_config,
                        'matches_expected': set(cors_config) == set(self.authorized_origins)
                    }
                    
                    if set(cors_config) == set(self.authorized_origins):
                        logger.info("✅ CORS configuration matches expected origins")
                        test_result['status'] = 'passed'
                    else:
                        logger.warning("⚠️  CORS configuration doesn't match expected origins")
                        test_result['status'] = 'warning'
                        test_result['recommendations'].append(
                            f"Expected origins: {self.authorized_origins}"
                        )
                        test_result['recommendations'].append(
                            f"Actual origins: {cors_config}"
                        )
                except json.JSONDecodeError:
                    logger.warning("⚠️  Could not parse diagnostics response")
                    test_result['status'] = 'warning'
                    test_result['recommendations'].append(
                        "Could not retrieve CORS configuration from backend"
                    )
            else:
                logger.warning("⚠️  Diagnostics endpoint not available")
                test_result['status'] = 'warning'
                test_result['recommendations'].append(
                    "Consider enabling diagnostics endpoint for better monitoring"
                )
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️  Could not check CORS configuration: {e}")
            test_result['status'] = 'warning'
            test_result['details']['error'] = str(e)
            test_result['recommendations'].append(
                "Could not automatically verify CORS configuration"
            )
        
        return test_result
    
    def _test_authorized_origin(self, origin: str) -> Dict:
        """Test that an authorized origin can make CORS requests"""
        logger.info(f"✅ Testing authorized origin: {origin}")
        
        test_result = {
            'test_name': f'Authorized Origin Test: {origin}',
            'test_type': 'authorized_origin',
            'origin': origin,
            'status': 'unknown',
            'details': {},
            'recommendations': []
        }
        
        # Test preflight request
        preflight_result = self._make_preflight_request(origin)
        test_result['details']['preflight'] = preflight_result
        
        # Test actual request
        actual_result = self._make_cors_request(origin)
        test_result['details']['actual_request'] = actual_result
        
        # Evaluate results
        if (preflight_result.get('allowed', False) and 
            actual_result.get('success', False) and
            actual_result.get('cors_headers', {}).get('access-control-allow-origin') == origin):
            
            logger.info(f"✅ {origin} - CORS requests allowed correctly")
            test_result['status'] = 'passed'
        else:
            logger.error(f"❌ {origin} - CORS requests not working properly")
            test_result['status'] = 'failed'
            test_result['recommendations'].append(
                f"Add {origin} to BACKEND_CORS_ORIGINS environment variable"
            )
        
        return test_result
    
    def _test_unauthorized_origin(self, origin: str) -> Dict:
        """Test that an unauthorized origin is blocked"""
        logger.info(f"🚫 Testing unauthorized origin: {origin}")
        
        test_result = {
            'test_name': f'Unauthorized Origin Test: {origin}',
            'test_type': 'unauthorized_origin',
            'origin': origin,
            'status': 'unknown',
            'details': {},
            'recommendations': []
        }
        
        # Test preflight request
        preflight_result = self._make_preflight_request(origin)
        test_result['details']['preflight'] = preflight_result
        
        # Test actual request
        actual_result = self._make_cors_request(origin)
        test_result['details']['actual_request'] = actual_result
        
        # Evaluate results - unauthorized origins should be blocked
        cors_header = actual_result.get('cors_headers', {}).get('access-control-allow-origin')
        
        if cors_header == origin:
            logger.error(f"❌ {origin} - Unauthorized origin was allowed!")
            test_result['status'] = 'failed'
            test_result['recommendations'].append(
                f"SECURITY ISSUE: {origin} should not be allowed. Check CORS configuration."
            )
        elif cors_header is None or cors_header == '':
            logger.info(f"✅ {origin} - Correctly blocked (no CORS header)")
            test_result['status'] = 'passed'
        else:
            logger.warning(f"⚠️  {origin} - Unexpected CORS header: {cors_header}")
            test_result['status'] = 'warning'
            test_result['recommendations'].append(
                f"Unexpected Access-Control-Allow-Origin header: {cors_header}"
            )
        
        return test_result
    
    def _make_preflight_request(self, origin: str) -> Dict:
        """Make a CORS preflight request"""
        try:
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'authorization,content-type'
            }
            
            response = requests.options(f"{self.backend_url}/api/v1/auth/me", 
                                      headers=headers, timeout=10)
            
            cors_headers = {
                key.lower(): value for key, value in response.headers.items()
                if key.lower().startswith('access-control')
            }
            
            return {
                'status_code': response.status_code,
                'allowed': response.status_code in [200, 204],
                'cors_headers': cors_headers,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'allowed': False
            }
    
    def _make_cors_request(self, origin: str) -> Dict:
        """Make an actual CORS request"""
        try:
            headers = {
                'Origin': origin,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.backend_url}/health", 
                                  headers=headers, timeout=10)
            
            cors_headers = {
                key.lower(): value for key, value in response.headers.items()
                if key.lower().startswith('access-control')
            }
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'cors_headers': cors_headers,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _update_summary(self, summary: Dict, test_result: Dict):
        """Update the test summary with results from a test"""
        summary['total_tests'] += 1
        
        if test_result['status'] == 'passed':
            summary['passed'] += 1
        elif test_result['status'] == 'failed':
            summary['failed'] += 1
        elif test_result['status'] == 'warning':
            summary['warnings'] += 1
    
    def _print_summary_report(self, results: Dict):
        """Print a formatted summary report"""
        summary = results['summary']
        
        logger.info("=" * 60)
        logger.info("📊 CORS VERIFICATION SUMMARY REPORT")
        logger.info("=" * 60)
        logger.info(f"🔗 Backend URL: {results['backend_url']}")
        logger.info(f"✅ Authorized Origins: {len(results['authorized_origins'])}")
        logger.info("")
        logger.info("📈 Test Results:")
        logger.info(f"  • Total Tests: {summary['total_tests']}")
        logger.info(f"  • ✅ Passed: {summary['passed']}")
        logger.info(f"  • ❌ Failed: {summary['failed']}")
        logger.info(f"  • ⚠️  Warnings: {summary['warnings']}")
        
        # Overall status
        if summary['failed'] == 0:
            if summary['warnings'] == 0:
                logger.info("")
                logger.info("🎉 CORS CONFIGURATION IS WORKING CORRECTLY!")
                logger.info("✅ All authorized origins are allowed")
                logger.info("✅ All unauthorized origins are blocked")
            else:
                logger.info("")
                logger.info("⚠️  CORS CONFIGURATION HAS WARNINGS")
                logger.info("🔍 Review warnings above for potential improvements")
        else:
            logger.info("")
            logger.info("❌ CORS CONFIGURATION ISSUES DETECTED!")
            logger.info("🚨 SECURITY RISK: Review failed tests immediately")
        
        # Detailed recommendations
        recommendations = []
        for test in results['tests']:
            recommendations.extend(test.get('recommendations', []))
        
        if recommendations:
            logger.info("")
            logger.info("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(set(recommendations), 1):
                logger.info(f"  {i}. {rec}")
        
        logger.info("=" * 60)


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(
        description='Verify CORS configuration for DrFirst Business Case Generator'
    )
    parser.add_argument(
        '--backend-url', 
        required=False,
        help='Backend URL (e.g., https://your-backend.run.app)'
    )
    parser.add_argument(
        '--frontend-url',
        required=False, 
        help='Authorized frontend URL (e.g., https://your-frontend.web.app)'
    )
    parser.add_argument(
        '--authorized-origins',
        nargs='*',
        help='List of authorized origins to test'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='Test local development setup'
    )
    parser.add_argument(
        '--output',
        help='Save detailed results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Determine configuration
    if args.local:
        backend_url = 'http://localhost:8000'
        authorized_origins = [
            'http://localhost:4000',
            'http://localhost:4002', 
            'http://localhost:4003',
            'http://127.0.0.1:4000',
            'http://127.0.0.1:4002'
        ]
    else:
        if not args.backend_url:
            logger.error("❌ Backend URL is required (use --backend-url or --local)")
            sys.exit(1)
        
        backend_url = args.backend_url
        
        if args.authorized_origins:
            authorized_origins = args.authorized_origins
        elif args.frontend_url:
            authorized_origins = [args.frontend_url]
        else:
            # Default production origins
            authorized_origins = [
                'https://drfirst-business-case-gen.web.app',
                'https://drfirst-business-case-gen.firebaseapp.com'
            ]
    
    # Run verification
    verifier = CorsVerifier(backend_url, authorized_origins)
    results = verifier.verify_cors_configuration()
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"📁 Detailed results saved to {args.output}")
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    elif results['summary']['warnings'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main() 