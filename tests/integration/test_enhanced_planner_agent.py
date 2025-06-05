#!/usr/bin/env python3
"""
Test script for the enhanced PlannerAgent that uses AI-powered effort estimation.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.agents.planner_agent import PlannerAgent


async def test_enhanced_planner_agent():
    """Test the enhanced PlannerAgent with different complexity scenarios."""
    
    print("🧪 Testing Enhanced PlannerAgent...")
    print("=" * 60)
    
    # Initialize the agent
    planner = PlannerAgent()
    
    # Test Case 1: Simple project
    print("\n🔬 Test Case 1: Simple Healthcare Dashboard")
    print("-" * 40)
    
    simple_prd = """
    # Healthcare Dashboard PRD
    
    ## Overview
    Create a simple dashboard for viewing patient statistics.
    
    ## Features
    - Basic patient list
    - Simple charts for patient demographics
    - User authentication
    - Basic reporting
    
    ## Technical Requirements
    - Web application
    - Database for patient data
    - Basic CRUD operations
    """
    
    simple_system_design = """
    # System Design: Healthcare Dashboard
    
    ## Architecture
    - Frontend: React.js
    - Backend: Node.js with Express
    - Database: PostgreSQL
    - Authentication: JWT tokens
    
    ## Components
    - User management
    - Patient data service
    - Reporting service
    """
    
    result1 = await planner.estimate_effort(simple_prd, simple_system_design, "Simple Healthcare Dashboard")
    print_result(result1, "Simple Project")
    
    # Test Case 2: Complex project with integrations
    print("\n🔬 Test Case 2: Complex EHR Integration Platform")
    print("-" * 40)
    
    complex_prd = """
    # EHR Integration Platform PRD
    
    ## Overview
    Develop a comprehensive platform for integrating multiple EHR systems with real-time data synchronization,
    machine learning analytics, and mobile applications.
    
    ## Features
    - HL7 FHIR integration with multiple EHR systems
    - Real-time data synchronization
    - Machine learning for predictive analytics
    - Mobile application for iOS and Android
    - Advanced reporting and dashboards
    - HIPAA compliant security
    - API integration with third-party systems
    - Natural language processing for clinical notes
    - Microservices architecture
    - Load balancing and scalability
    - Payment processing integration
    - Blockchain for data integrity
    
    ## Technical Requirements
    - Distributed microservices architecture
    - Real-time messaging system
    - Advanced encryption and security
    - Performance monitoring and logging
    - Scalable cloud infrastructure
    """
    
    complex_system_design = """
    # System Design: EHR Integration Platform
    
    ## Architecture
    - Microservices with Docker containers
    - Kubernetes orchestration
    - API Gateway with rate limiting
    - Message queues (Apache Kafka)
    - Distributed caching (Redis)
    - Load balancing (NGINX)
    - Monitoring (Prometheus + Grafana)
    
    ## Security
    - OAuth 2.0 + OpenID Connect
    - End-to-end encryption
    - HIPAA compliance framework
    - Audit logging
    
    ## Integrations
    - HL7 FHIR APIs
    - Multiple EHR systems (Epic, Cerner, Allscripts)
    - Payment processing (Stripe)
    - Cloud services (AWS/Azure)
    - Machine learning pipelines
    - Mobile API endpoints
    
    ## Data Layer
    - Primary database: PostgreSQL cluster
    - Analytics database: Apache Cassandra
    - Caching: Redis cluster
    - Search: Elasticsearch
    """
    
    result2 = await planner.estimate_effort(complex_prd, complex_system_design, "Complex EHR Integration Platform")
    print_result(result2, "Complex Project")
    
    # Test Case 3: Minimal content (edge case)
    print("\n🔬 Test Case 3: Minimal Content")
    print("-" * 40)
    
    minimal_prd = "Basic healthcare app for appointment scheduling."
    minimal_system_design = "Simple web app with database."
    
    result3 = await planner.estimate_effort(minimal_prd, minimal_system_design, "Minimal Healthcare App")
    print_result(result3, "Minimal Project")
    
    # Test Case 4: Medium complexity project
    print("\n🔬 Test Case 4: Medium Complexity Telemedicine Platform")
    print("-" * 40)
    
    medium_prd = """
    # Telemedicine Platform PRD
    
    ## Overview
    Develop a telemedicine platform for virtual consultations with video calling,
    appointment scheduling, and basic EHR integration.
    
    ## Features
    - Video calling for consultations
    - Appointment scheduling system
    - Patient portal with basic medical records
    - Provider dashboard
    - Payment integration
    - Email notifications
    - Basic reporting
    - HIPAA compliance
    - Mobile responsive web application
    
    ## Technical Requirements
    - Web application with responsive design
    - Video calling integration (WebRTC or third-party)
    - Database for user and appointment data
    - Payment processing
    - Email service integration
    - Basic API for mobile access
    """
    
    medium_system_design = """
    # System Design: Telemedicine Platform
    
    ## Architecture
    - Frontend: React.js with responsive design
    - Backend: Python Django REST API
    - Database: PostgreSQL
    - Video: Twilio Video API integration
    - Payment: Stripe integration
    - Email: SendGrid integration
    
    ## Components
    - User authentication and authorization
    - Appointment management service
    - Video calling service
    - Payment processing service
    - Notification service
    - Basic admin panel
    """
    
    result4 = await planner.estimate_effort(medium_prd, medium_system_design, "Telemedicine Platform")
    print_result(result4, "Medium Complexity Project")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced PlannerAgent testing completed!")


def print_result(result, project_type):
    """Helper function to print test results in a readable format."""
    
    if result['status'] == 'success':
        effort_data = result['effort_breakdown']
        print(f"✅ {project_type} - Status: {result['status']}")
        print(f"📊 Total Hours: {effort_data['total_hours']}")
        print(f"⏱️ Duration: {effort_data['estimated_duration_weeks']} weeks")
        print(f"🎯 Complexity: {effort_data['complexity_assessment']}")
        print(f"📝 Notes: {effort_data['notes']}")
        print("\n👥 Role Breakdown:")
        for role in effort_data['roles']:
            print(f"  • {role['role']}: {role['hours']} hours")
        print(f"🤖 Method: {result['message']}")
    else:
        print(f"❌ {project_type} - Status: {result['status']}")
        print(f"💬 Error: {result['message']}")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_enhanced_planner_agent()) 