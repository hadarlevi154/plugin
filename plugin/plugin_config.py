from dataclasses import dataclass


@dataclass
class PluginConfig:
    """Configuration for plugin"""
    username: str
    password: str
    api_base_url: str