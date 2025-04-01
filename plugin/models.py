from dataclasses import dataclass
from typing import Dict, Any, Optional
from plugin.constants import ConstantsParameters

@dataclass
class EvidenceResult:
    """Result of an evidence collection"""
    success: bool
    data: Dict[str, Any] = None
    message: str = ""
    status_code: int = 0

    @classmethod
    def success_result(cls, data: Dict[str, Any], message: str = "Success") -> 'EvidenceResult':
        """Successful evidence result"""
        return cls(success=True, data=data, message=message, status_code=ConstantsParameters.OK)

    @classmethod
    def failure_result(cls, message: str, status_code: int = 0,
                       data: Optional[Dict[str, Any]] = None) -> 'EvidenceResult':
        """Failed evidence result"""
        return cls(success=False, data=data, message=message, status_code=status_code)


@dataclass
class ConnectivityResult:
    """Result of connectivity test"""
    success: bool
    message: str
    token: Optional[str] = None
    status_code: int = 0

    @classmethod
    def success_result(cls, message: str, token: str) -> 'ConnectivityResult':
        """Successful connectivity result"""
        return cls(success=True, message=message, token=token, status_code=ConstantsParameters.OK)

    @classmethod
    def failure_result(cls, message: str, status_code: int = 0) -> 'ConnectivityResult':
        """Failed connectivity result"""
        return cls(success=False, message=message, status_code=status_code)