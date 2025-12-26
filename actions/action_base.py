"""
Home-Alexa - Action Base
Clase base para todas las acciones del asistente
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum


class ActionCategory(Enum):
    """Categorías de acciones."""
    SYSTEM = "system"
    FILES = "files"
    BROWSER = "browser"
    MEDIA = "media"
    TERMINAL = "terminal"
    UTILITIES = "utilities"


class RiskLevel(Enum):
    """Nivel de riesgo de una acción."""
    SAFE = "safe"           # No requiere confirmación
    MODERATE = "moderate"   # Confirmación opcional
    CRITICAL = "critical"   # Siempre requiere confirmación


@dataclass
class ActionResult:
    """Resultado de la ejecución de una acción."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error
        }


@dataclass
class ActionMetadata:
    """Metadatos de una acción."""
    name: str
    description: str
    description_en: str
    category: ActionCategory
    risk_level: RiskLevel
    keywords_es: List[str] = field(default_factory=list)
    keywords_en: List[str] = field(default_factory=list)
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)


class ActionBase(ABC):
    """
    Clase base abstracta para todas las acciones del asistente.

    Cada acción debe:
    1. Definir sus metadatos (nombre, descripción, categoría, riesgo)
    2. Implementar validate_params() para validar parámetros
    3. Implementar execute() para ejecutar la acción
    """

    # Metadatos - deben ser sobrescritos por subclases
    metadata: ActionMetadata = ActionMetadata(
        name="base_action",
        description="Acción base (no usar directamente)",
        description_en="Base action (do not use directly)",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE
    )

    def __init__(self):
        """Inicializa la acción."""
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Ejecuta la acción con los parámetros dados.

        Args:
            params: Diccionario con los parámetros de la acción

        Returns:
            ActionResult con el resultado de la ejecución
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> tuple:
        """
        Valida que los parámetros sean correctos.

        Args:
            params: Parámetros a validar

        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Verificar parámetros requeridos
        for required in self.metadata.required_params:
            if required not in params:
                return False, f"Falta parámetro requerido: {required}"

        return True, ""

    def get_confirmation_message(self, params: Dict[str, Any], language: str = "es") -> str:
        """
        Genera el mensaje de confirmación para la acción.

        Args:
            params: Parámetros de la acción
            language: Idioma del mensaje

        Returns:
            Mensaje de confirmación
        """
        if language == "en":
            return f"Do you want to execute: {self.metadata.description_en}?"
        return f"¿Deseas ejecutar: {self.metadata.description}?"

    @property
    def name(self) -> str:
        """Nombre de la acción."""
        return self.metadata.name

    @property
    def category(self) -> ActionCategory:
        """Categoría de la acción."""
        return self.metadata.category

    @property
    def risk_level(self) -> RiskLevel:
        """Nivel de riesgo de la acción."""
        return self.metadata.risk_level

    @property
    def requires_confirmation(self) -> bool:
        """Si la acción requiere confirmación."""
        return self.metadata.risk_level == RiskLevel.CRITICAL

    def __str__(self) -> str:
        return f"Action({self.name})"

    def __repr__(self) -> str:
        return self.__str__()
