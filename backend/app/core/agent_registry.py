"""
Agent Registry for managing agent instances and coordinating function calls
"""

from typing import Dict, Any, Optional
import logging
from ..agents.product_manager_agent import ProductManagerAgent
from ..agents.architect_agent import ArchitectAgent
from ..agents.planner_agent import PlannerAgent
from ..agents.cost_analyst_agent import CostAnalystAgent
from ..agents.sales_value_analyst_agent import SalesValueAnalystAgent
from ..agents.financial_model_agent import FinancialModelAgent
from ..services.prompt_service import PromptService
from google.cloud import firestore


class AgentRegistry:
    """Registry for managing agent instances"""
    
    def __init__(self, db: firestore.Client = None):
        self.agents: Dict[str, Any] = {}
        self.db = db or firestore.Client()
        self.prompt_service = PromptService(self.db)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agent instances"""
        try:
            # Initialize Product Manager Agent
            self.agents["ProductManagerAgent"] = ProductManagerAgent(
                prompt_service=self.prompt_service
            )
            
            # Initialize Architect Agent
            self.agents["ArchitectAgent"] = ArchitectAgent()
            
            # Initialize Planner Agent
            self.agents["PlannerAgent"] = PlannerAgent()
            
            # Initialize Cost Analyst Agent
            self.agents["CostAnalystAgent"] = CostAnalystAgent()
            
            # Initialize Sales Value Analyst Agent
            self.agents["SalesValueAnalystAgent"] = SalesValueAnalystAgent()
            
            # Initialize Financial Model Agent
            self.agents["FinancialModelAgent"] = FinancialModelAgent()
            
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            raise
    
    def get_agent(self, agent_class: str) -> Optional[Any]:
        """Get an agent instance by class name"""
        return self.agents.get(agent_class)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all agent instances"""
        return self.agents
    
    def get_agent_status(self, agent_class: str) -> Dict[str, Any]:
        """Get status information for an agent"""
        agent = self.get_agent(agent_class)
        if not agent:
            return {"status": "not_found", "agent_class": agent_class}
        
        # Try to get status method if it exists
        if hasattr(agent, 'get_status'):
            return agent.get_status()
        
        return {
            "status": "initialized",
            "agent_class": agent_class,
            "available": True
        }
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all agents"""
        return {
            agent_class: self.get_agent_status(agent_class)
            for agent_class in self.agents.keys()
        }
    
    def reinitialize_agent(self, agent_class: str) -> bool:
        """Reinitialize a specific agent"""
        try:
            if agent_class == "ProductManagerAgent":
                self.agents[agent_class] = ProductManagerAgent(
                    prompt_service=self.prompt_service
                )
            elif agent_class == "ArchitectAgent":
                self.agents[agent_class] = ArchitectAgent()
            elif agent_class == "PlannerAgent":
                self.agents[agent_class] = PlannerAgent()
            elif agent_class == "CostAnalystAgent":
                self.agents[agent_class] = CostAnalystAgent()
            elif agent_class == "SalesValueAnalystAgent":
                self.agents[agent_class] = SalesValueAnalystAgent()
            elif agent_class == "FinancialModelAgent":
                self.agents[agent_class] = FinancialModelAgent()
            else:
                return False
            
            self.logger.info(f"Reinitialized agent: {agent_class}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reinitializing agent {agent_class}: {str(e)}")
            return False


# Global registry instance
_global_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry(db: firestore.Client = None) -> AgentRegistry:
    """Get the global agent registry instance"""
    global _global_agent_registry
    
    if _global_agent_registry is None:
        _global_agent_registry = AgentRegistry(db=db)
    
    return _global_agent_registry


def reset_agent_registry():
    """Reset the global agent registry (useful for testing)"""
    global _global_agent_registry
    _global_agent_registry = None 