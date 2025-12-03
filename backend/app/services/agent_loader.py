"""Agent configuration loader from YAML files."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


class AgentLoader:
    """Load and cache agent configurations from YAML files."""

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize the agent loader.

        Args:
            config_dir: Path to the agents config directory.
                       Defaults to backend/configs/agents/
        """
        if config_dir is None:
            # Default to backend/configs/agents/
            self._config_dir = Path(__file__).parent.parent.parent / "configs" / "agents"
        else:
            self._config_dir = config_dir

    @property
    def config_dir(self) -> Path:
        """Get the config directory path."""
        return self._config_dir

    @lru_cache(maxsize=32)
    def load_agent(self, slug: str) -> dict[str, Any] | None:
        """Load agent configuration by slug.

        Args:
            slug: The agent slug (e.g., 'general', 'hr', 'mental-health')

        Returns:
            Agent configuration dict or None if not found
        """
        # Try with slug as-is, then with underscore replacement
        possible_names = [slug, slug.replace("-", "_")]

        for name in possible_names:
            config_file = self._config_dir / f"{name}.yaml"
            if config_file.exists():
                return self._load_yaml(config_file)

        return None

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """Load and parse a YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Parsed YAML content as dict
        """
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @lru_cache(maxsize=1)
    def list_agents(self) -> list[dict[str, Any]]:
        """List all available agents.

        Returns:
            List of agent info dicts with basic metadata
        """
        agents = []

        if not self._config_dir.exists():
            return agents

        for yaml_file in sorted(self._config_dir.glob("*.yaml")):
            config = self._load_yaml(yaml_file)
            if config and "agent" in config:
                agent_info = config["agent"].copy()
                # Add tools and settings info
                agent_info["tools"] = config.get("tools", [])
                agent_info["settings"] = config.get("settings", {})
                if "privacy" in config:
                    agent_info["privacy"] = config["privacy"]
                agents.append(agent_info)

        return agents

    @lru_cache(maxsize=32)
    def get_system_prompt(self, slug: str) -> str | None:
        """Get the system prompt for an agent.

        Args:
            slug: The agent slug

        Returns:
            System prompt string or None if not found
        """
        config = self.load_agent(slug)
        if config and "persona" in config:
            return config["persona"].get("system_prompt")
        return None

    def get_agent_settings(self, slug: str) -> dict[str, Any]:
        """Get agent settings (temperature, max_tokens, etc).

        Args:
            slug: The agent slug

        Returns:
            Settings dict or empty dict if not found
        """
        config = self.load_agent(slug)
        if config:
            return config.get("settings", {})
        return {}

    def get_agent_tools(self, slug: str) -> list[str]:
        """Get list of tools available to an agent.

        Args:
            slug: The agent slug

        Returns:
            List of tool names
        """
        config = self.load_agent(slug)
        if config:
            return config.get("tools", [])
        return []

    def clear_cache(self) -> None:
        """Clear all cached configurations."""
        self.load_agent.cache_clear()
        self.list_agents.cache_clear()
        self.get_system_prompt.cache_clear()


# Singleton instance
agent_loader = AgentLoader()
