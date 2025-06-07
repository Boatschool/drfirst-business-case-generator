"""
Agent Registry for managing agent instances and coordinating function calls
"""

from typing import Dict, Any, Optional
import logging
from google.cloud import firestore


class AgentRegistry:
    """Registry for managing agent instances with lazy initialization"""
    
    def __init__(self, db: firestore.Client = None):
        self.agents: Dict[str, Any] = {}
        self.db = db or firestore.Client()
        self._prompt_service = None
        self.logger = logging.getLogger(__name__)
        
        # Don't initialize agents at startup - use lazy initialization
        self.logger.info("AgentRegistry initialized with lazy loading")
    
    @property
    def prompt_service(self):
        """Lazy initialization of prompt service"""
        if self._prompt_service is None:
            from ..services.prompt_service import PromptService
            self._prompt_service = PromptService(self.db)
        return self._prompt_service
    
    def _initialize_agent(self, agent_class: str) -> Any:
        """Initialize a specific agent on demand"""
        try:
            self.logger.info(f"Lazy initializing agent: {agent_class}")
            
            if agent_class == "ProductManagerAgent":
                from ..agents.product_manager_agent import ProductManagerAgent
                agent = ProductManagerAgent(prompt_service=self.prompt_service)
            elif agent_class == "ArchitectAgent":
                from ..agents.architect_agent import ArchitectAgent
                agent = ArchitectAgent()
            elif agent_class == "PlannerAgent":
                from ..agents.planner_agent import PlannerAgent
                agent = PlannerAgent()
            elif agent_class == "CostAnalystAgent":
                from ..agents.cost_analyst_agent import CostAnalystAgent
                agent = CostAnalystAgent()
            elif agent_class == "SalesValueAnalystAgent":
                from ..agents.sales_value_analyst_agent import SalesValueAnalystAgent
                agent = SalesValueAnalystAgent()
            elif agent_class == "FinancialModelAgent":
                from ..agents.financial_model_agent import FinancialModelAgent
                agent = FinancialModelAgent()
            else:
                raise ValueError(f"Unknown agent class: {agent_class}")
            
            self.agents[agent_class] = agent
            self.logger.info(f"Successfully initialized agent: {agent_class}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Error initializing agent {agent_class}: {str(e)}")
            raise
    
    def get_agent(self, agent_class: str) -> Optional[Any]:
        """Get an agent instance by class name with lazy initialization"""
        if agent_class not in self.agents:
            self._initialize_agent(agent_class)
        return self.agents.get(agent_class)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all agent instances, initializing them if needed"""
        agent_classes = [
            "ProductManagerAgent", "ArchitectAgent", "PlannerAgent",
            "CostAnalystAgent", "SalesValueAnalystAgent", "FinancialModelAgent"
        ]
        
        for agent_class in agent_classes:
            if agent_class not in self.agents:
                self._initialize_agent(agent_class)
        
        return self.agents
    
    def get_agent_status(self, agent_class: str) -> Dict[str, Any]:
        """Get status information for an agent"""
        # Don't initialize agent just to get status
        if agent_class not in self.agents:
            return {
                "status": "not_initialized", 
                "agent_class": agent_class,
                "available": False
            }
        
        agent = self.agents[agent_class]
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
        """Get status for all agents without forcing initialization"""
        agent_classes = [
            "ProductManagerAgent", "ArchitectAgent", "PlannerAgent",
            "CostAnalystAgent", "SalesValueAnalystAgent", "FinancialModelAgent"
        ]
        
        return {
            agent_class: self.get_agent_status(agent_class)
            for agent_class in agent_classes
        }
    
    def reinitialize_agent(self, agent_class: str) -> bool:
        """Reinitialize a specific agent"""
        try:
            # Remove existing agent if it exists
            if agent_class in self.agents:
                del self.agents[agent_class]
            
            # Initialize fresh agent
            self._initialize_agent(agent_class)
            return True
            
        except Exception as e:
            self.logger.error(f"Error reinitializing agent {agent_class}: {str(e)}")
            return False


# Global registry instance with lazy initialization
_global_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry(db: firestore.Client = None) -> AgentRegistry:
    """Get the global agent registry instance with lazy initialization"""
    global _global_agent_registry
    
    if _global_agent_registry is None:
        _global_agent_registry = AgentRegistry(db=db)
    
    return _global_agent_registry


def reset_agent_registry():
    """Reset the global agent registry (useful for testing)"""
    global _global_agent_registry
    _global_agent_registry = None 