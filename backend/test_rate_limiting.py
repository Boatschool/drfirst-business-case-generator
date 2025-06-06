#!/usr/bin/env python3
"""
Simple script to test API rate limiting functionality.

This script sends rapid requests to rate-limited endpoints to verify
that the rate limiting is working correctly.
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Tuple


class RateLimitTester:
    """Simple rate limit testing utility."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET") -> Tuple[int, dict, float]:
        """
        Make a single request and return status code, response data, and time taken.
        
        Returns:
            Tuple of (status_code, response_data, request_time)
        """
        start_time = time.time()
        
        try:
            async with self.session.request(method, f"{self.base_url}{endpoint}") as response:
                end_time = time.time()
                request_time = end_time - start_time
                
                try:
                    data = await response.json()
                except Exception:
                    data = {"text": await response.text()}
                
                return response.status, data, request_time
        except Exception as e:
            end_time = time.time()
            request_time = end_time - start_time
            return 0, {"error": str(e)}, request_time
    
    async def test_endpoint_rate_limit(
        self, 
        endpoint: str, 
        num_requests: int = 10, 
        delay_between_requests: float = 0.1
    ) -> List[Tuple[int, dict, float]]:
        """
        Test rate limiting by sending multiple rapid requests to an endpoint.
        
        Args:
            endpoint: API endpoint to test
            num_requests: Number of requests to send
            delay_between_requests: Delay in seconds between requests
            
        Returns:
            List of (status_code, response_data, request_time) tuples
        """
        print(f"\nTesting rate limiting for {endpoint}")
        print(f"Sending {num_requests} requests with {delay_between_requests}s delay...")
        
        results = []
        
        for i in range(num_requests):
            result = await self.make_request(endpoint)
            results.append(result)
            
            status_code, response_data, request_time = result
            
            print(f"Request {i+1:2d}: {status_code} - {request_time:.3f}s", end="")
            
            if status_code == 429:
                print(" [RATE LIMITED]")
                if "Retry-After" in str(response_data):
                    print(f"    Rate limit response: {response_data}")
            elif status_code == 200:
                print(" [SUCCESS]")
            else:
                print(f" [ERROR: {response_data.get('error', 'Unknown')}]")
            
            if i < num_requests - 1:  # Don't delay after the last request
                await asyncio.sleep(delay_between_requests)
        
        return results
    
    def analyze_results(self, results: List[Tuple[int, dict, float]], endpoint: str):
        """Analyze and print results of rate limit testing."""
        print(f"\n=== Analysis for {endpoint} ===")
        
        success_count = len([r for r in results if r[0] == 200])
        rate_limited_count = len([r for r in results if r[0] == 429])
        error_count = len([r for r in results if r[0] not in [200, 429]])
        
        print(f"Total requests: {len(results)}")
        print(f"Successful (200): {success_count}")
        print(f"Rate limited (429): {rate_limited_count}")
        print(f"Other errors: {error_count}")
        
        if rate_limited_count > 0:
            print("✅ Rate limiting is working!")
            first_rate_limit = next(i for i, r in enumerate(results) if r[0] == 429)
            print(f"   First rate limit at request #{first_rate_limit + 1}")
        else:
            print("❌ No rate limiting detected - check configuration")


async def main():
    """Main test function."""
    print("API Rate Limiting Test")
    print("=" * 50)
    
    async with RateLimitTester() as tester:
        # Test health endpoint (should not be rate limited)
        print("\n1. Testing health endpoint (should not be rate limited)")
        health_results = await tester.test_endpoint_rate_limit("/health", 5, 0.1)
        tester.analyze_results(health_results, "/health")
        
        # Test cases listing endpoint (rate limited to 50/minute)
        print("\n2. Testing cases listing endpoint (50/minute limit)")
        # Note: This requires authentication, so will likely return 401
        # but we can still test if rate limiting headers are present
        cases_results = await tester.test_endpoint_rate_limit("/api/v1/cases", 15, 0.1)
        tester.analyze_results(cases_results, "/api/v1/cases")
        
        # Test agents listing endpoint (may have default limits)
        print("\n3. Testing agents listing endpoint")
        agents_results = await tester.test_endpoint_rate_limit("/api/v1/agents/", 25, 0.1)
        tester.analyze_results(agents_results, "/api/v1/agents/")
        
        print("\n" + "=" * 50)
        print("Rate limiting test completed!")
        print("\nNote: Some endpoints may return 401 (Unauthorized) if authentication")
        print("is required, but rate limiting should still be applied before auth checks.")


if __name__ == "__main__":
    asyncio.run(main()) 