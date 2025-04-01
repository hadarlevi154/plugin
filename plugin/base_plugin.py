from abc import ABC, abstractmethod
from .models import ConnectivityResult, EvidenceResult
from .plugin_config import PluginConfig


class BasePlugin(ABC):

    def __init__(self, config: PluginConfig):
        """Initialize plugin with config"""
        self.config = config
        self.auth_token = None

    @abstractmethod
    def test_connectivity(self) -> ConnectivityResult:
        """Test connectivity to the API and authenticate"""
        pass

    @abstractmethod
    def collect_evidence(self, evidence_type: str, **kwargs) -> EvidenceResult:
        """Collect evidence"""
        pass