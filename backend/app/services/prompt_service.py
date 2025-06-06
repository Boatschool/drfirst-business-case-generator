"""
Service for managing configurable agent prompts.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from ..models.agent_prompt import (
    AgentPrompt,
    AgentPromptVersion,
    AgentPromptCreate,
    AgentPromptVersionCreate,
    AgentPromptUpdate,
)


class PromptService:
    """Service for managing agent prompts in Firestore."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "agentPrompts"
        self.logger = logging.getLogger(__name__)

    async def get_prompt_by_id(self, prompt_id: str) -> Optional[AgentPrompt]:
        """Get a prompt by its ID."""
        try:
            doc = self.db.collection(self.collection_name).document(prompt_id).get()
            if not doc.exists:
                return None

            data = doc.to_dict()
            data["prompt_id"] = doc.id
            return AgentPrompt(**data)
        except Exception as e:
            self.logger.info(f"Error getting prompt by ID {prompt_id}: {e}")
            return None

    async def get_prompt_by_agent_function(
        self, agent_name: str, agent_function: str
    ) -> Optional[AgentPrompt]:
        """Get the active prompt for a specific agent and function."""
        try:
            docs = (
                self.db.collection(self.collection_name)
                .where("agent_name", "==", agent_name)
                .where("agent_function", "==", agent_function)
                .where("is_enabled", "==", True)
                .limit(1)
                .stream()
            )

            for doc in docs:
                data = doc.to_dict()
                data["prompt_id"] = doc.id
                return AgentPrompt(**data)

            return None
        except Exception as e:
            self.logger.info(f"Error getting prompt for {agent_name}.{agent_function}: {e}")
            return None

    async def get_active_prompt_template(
        self, agent_name: str, agent_function: str
    ) -> Optional[str]:
        """Get the active prompt template for an agent function."""
        prompt = await self.get_prompt_by_agent_function(agent_name, agent_function)
        if not prompt:
            return None

        # Find the active version
        for version in prompt.versions:
            if version.is_active and version.version == prompt.current_version:
                return version.prompt_template

        return None

    async def render_prompt(
        self, agent_name: str, agent_function: str, variables: Dict[str, Any]
    ) -> Optional[str]:
        """Render a prompt template with the provided variables."""
        template = await self.get_active_prompt_template(agent_name, agent_function)
        if not template:
            return None

        try:
            # Simple string formatting - could be enhanced with Jinja2 for more complex templates
            rendered = template.format(**variables)

            # Update usage tracking
            await self._update_usage_tracking(agent_name, agent_function)

            return rendered
        except KeyError as e:
            self.logger.info(f"Missing variable in prompt template: {e}")
            return None
        except Exception as e:
            self.logger.info(f"Error rendering prompt: {e}")
            return None

    async def create_prompt(self, prompt_data: AgentPromptCreate, user_id: str) -> str:
        """Create a new agent prompt."""
        prompt_id = str(uuid.uuid4())

        # Create initial version
        initial_version = AgentPromptVersion(
            version="1.0.0",
            prompt_template=prompt_data.prompt_template,
            description=prompt_data.version_description,
            created_by=user_id,
            is_active=True,
        )

        # Create the prompt
        prompt = AgentPrompt(
            prompt_id=prompt_id,
            agent_name=prompt_data.agent_name,
            agent_function=prompt_data.agent_function,
            current_version="1.0.0",
            versions=[initial_version],
            title=prompt_data.title,
            description=prompt_data.description,
            category=prompt_data.category,
            placeholders=prompt_data.placeholders,
            ai_model_config=prompt_data.ai_model_config,
            created_by=user_id,
            last_updated_by=user_id,
        )

        # Save to Firestore
        doc_data = prompt.dict()
        doc_data.pop("prompt_id")  # Don't store ID in the document

        self.db.collection(self.collection_name).document(prompt_id).set(doc_data)

        return prompt_id

    async def add_prompt_version(
        self, prompt_id: str, version_data: AgentPromptVersionCreate, user_id: str
    ) -> bool:
        """Add a new version to an existing prompt."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(prompt_id)
            doc = doc_ref.get()

            if not doc.exists:
                return False

            prompt_data = doc.to_dict()
            prompt = AgentPrompt(prompt_id=prompt_id, **prompt_data)

            # Generate next version number
            current_versions = [v.version for v in prompt.versions]
            next_version = self._generate_next_version(current_versions)

            # Create new version
            new_version = AgentPromptVersion(
                version=next_version,
                prompt_template=version_data.prompt_template,
                description=version_data.description,
                created_by=user_id,
                is_active=version_data.make_active,
            )

            # If making this version active, deactivate others
            if version_data.make_active:
                for version in prompt.versions:
                    version.is_active = False
                prompt.current_version = next_version

            # Add new version
            prompt.versions.append(new_version)
            prompt.updated_at = datetime.now()
            prompt.last_updated_by = user_id

            # Update placeholders and model config if provided
            if version_data.placeholders:
                prompt.placeholders = version_data.placeholders
            if version_data.ai_model_config:
                prompt.ai_model_config = version_data.ai_model_config

            # Save updated prompt
            doc_data = prompt.dict()
            doc_data.pop("prompt_id")
            doc_ref.set(doc_data)

            return True
        except Exception as e:
            self.logger.info(f"Error adding prompt version: {e}")
            return False

    async def list_prompts(self, agent_name: Optional[str] = None) -> List[AgentPrompt]:
        """List all prompts, optionally filtered by agent name."""
        try:
            query = self.db.collection(self.collection_name)

            if agent_name:
                query = query.where("agent_name", "==", agent_name)

            docs = query.stream()
            prompts = []

            for doc in docs:
                data = doc.to_dict()
                data["prompt_id"] = doc.id
                prompts.append(AgentPrompt(**data))

            return prompts
        except Exception as e:
            self.logger.info(f"Error listing prompts: {e}")
            return []

    async def update_prompt(
        self, prompt_id: str, update_data: AgentPromptUpdate, user_id: str
    ) -> bool:
        """Update prompt metadata."""
        try:
            doc_ref = self.db.collection(self.collection_name).document(prompt_id)
            doc = doc_ref.get()

            if not doc.exists:
                return False

            update_dict = {}
            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.category is not None:
                update_dict["category"] = update_data.category
            if update_data.is_enabled is not None:
                update_dict["is_enabled"] = update_data.is_enabled
            if update_data.ai_model_config is not None:
                update_dict["ai_model_config"] = update_data.ai_model_config

            if update_dict:
                update_dict["updated_at"] = datetime.now()
                update_dict["last_updated_by"] = user_id
                doc_ref.update(update_dict)

            return True
        except Exception as e:
            self.logger.info(f"Error updating prompt: {e}")
            return False

    async def _update_usage_tracking(self, agent_name: str, agent_function: str):
        """Update usage tracking for a prompt."""
        try:
            docs = (
                self.db.collection(self.collection_name)
                .where("agent_name", "==", agent_name)
                .where("agent_function", "==", agent_function)
                .limit(1)
                .stream()
            )

            for doc in docs:
                doc_ref = self.db.collection(self.collection_name).document(doc.id)
                doc_ref.update(
                    {
                        "usage_count": firestore.Increment(1),
                        "last_used_at": datetime.now(),
                    }
                )
                break
        except Exception as e:
            self.logger.info(f"Error updating usage tracking: {e}")

    def _generate_next_version(self, existing_versions: List[str]) -> str:
        """Generate the next version number."""
        if not existing_versions:
            return "1.0.0"

        # Simple version increment - could be more sophisticated
        latest_versions = sorted(existing_versions, reverse=True)
        latest = latest_versions[0]

        try:
            parts = latest.split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{major}.{minor}.{patch + 1}"
        except:
            return "1.0.0"
