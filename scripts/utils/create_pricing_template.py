#!/usr/bin/env python3
"""
Simple script to create a pricing template in Firestore
"""

import asyncio
from google.cloud import firestore
from app.core.config import settings

async def create_template():
    """Create a default pricing template"""
    db = firestore.Client(project=settings.firebase_project_id)
    
    template_data = {
        'name': 'Default Value Projection Template V1',
        'description': 'Placeholder template for initial value scenarios in healthcare technology projects',
        'isActive': True,
        'version': '1.0',
        'structureDefinition': {
            'type': 'LowBaseHigh',
            'scenarios': [
                {'case': 'Low', 'value': 5000, 'description': 'Conservative estimate'},
                {'case': 'Base', 'value': 15000, 'description': 'Most likely estimate'},
                {'case': 'High', 'value': 30000, 'description': 'Optimistic estimate'}
            ]
        },
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    template_ref = db.collection('pricingTemplates').document('default_value_projection')
    await asyncio.to_thread(template_ref.set, template_data)
    print('✅ Created pricing template successfully')

if __name__ == "__main__":
    asyncio.run(create_template()) 