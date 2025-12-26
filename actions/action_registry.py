"""
Home-Alexa - Action Registry
Registro central de todas las acciones disponibles
"""

from typing import Dict, Type, Optional, List
from actions.action_base import ActionBase, ActionCategory, ActionMetadata
from utils.logger import get_logger

logger = get_logger(__name__)


class ActionRegistry:
    """
    Registro singleton de todas las acciones del asistente.
    Permite registrar, buscar y listar acciones.
    """

    _instance: Optional['ActionRegistry'] = None
    _actions: Dict[str, Type[ActionBase]] = {}
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not ActionRegistry._initialized:
            ActionRegistry._initialized = True
            self._load_builtin_actions()

    def _load_builtin_actions(self) -> None:
        """Carga las acciones incorporadas."""
        # Importar y registrar acciones de cada categoría
        try:
            from actions.system.open_app import OpenAppAction
            from actions.system.volume_control import (
                VolumeSetAction, VolumeUpAction,
                VolumeDownAction, VolumeMuteAction
            )
            from actions.browser.browser_control import (
                BrowserOpenUrlAction, BrowserSearchAction,
                BrowserNewTabAction, BrowserCloseTabAction
            )
            from actions.media.media_control import (
                MediaPlayAction, MediaPauseAction, MediaPlayPauseAction,
                MediaNextAction, MediaPreviousAction, YouTubeSkipAdAction
            )
            from actions.terminal.command_runner import TerminalRunAction
            from actions.utilities.timer_manager import (
                TimerSetAction, AlarmSetAction, ReminderSetAction
            )
            from actions.utilities.conversation import NoAction
            from actions.system.silent_mode_action import SilentModeAction  # v6.1
            from actions.system.undo_action import UndoAction  # v6.1
            from actions.productivity.voice_notes_action import VoiceNotesAction  # v6.1
            from actions.vision.camera_vision_action import CameraVisionAction  # v6.1
            from actions.vision.ocr_action import OCRAction  # v6.1
            from actions.automation.scheduler_action import SchedulerAction  # v6.1
            from actions.automation.triggers_action import TriggersAction  # v6.1
            from actions.automation.macros_action import MacrosAction  # v6.1
            from actions.productivity.dictation_action import DictationAction  # v6.1
            from actions.productivity.file_search_action import FileSearchAction  # v6.1
            from actions.productivity.ide_control_action import IDEControlAction  # v6.1

            # Registrar todas las acciones
            actions_to_register = [
                OpenAppAction,
                VolumeSetAction, VolumeUpAction, VolumeDownAction, VolumeMuteAction,
                BrowserOpenUrlAction, BrowserSearchAction,
                BrowserNewTabAction, BrowserCloseTabAction,
                MediaPlayAction, MediaPauseAction, MediaPlayPauseAction,
                MediaNextAction, MediaPreviousAction, YouTubeSkipAdAction,
                TerminalRunAction,
                TimerSetAction, AlarmSetAction, ReminderSetAction,
                NoAction,
                SilentModeAction,  # v6.1 - Silent mode
                UndoAction,  # v6.1 - Undo last action
                VoiceNotesAction,  # v6.1 - Voice notes
                CameraVisionAction,  # v6.1 - Camera vision
                OCRAction,  # v6.1 - OCR text extraction
                SchedulerAction,  # v6.1 - Scheduled routines
                TriggersAction,  # v6.1 - Conditional triggers
                MacrosAction,  # v6.1 - Macro recording
                DictationAction,  # v6.1 - Universal dictation
                FileSearchAction,  # v6.1 - File search
                IDEControlAction,  # v6.1 - IDE control
            ]

            for action_class in actions_to_register:
                self.register(action_class)

            logger.info(f"Acciones registradas: {len(self._actions)}")

        except ImportError as e:
            logger.warning(f"Error importando acciones: {e}")

    @classmethod
    def register(cls, action_class: Type[ActionBase]) -> None:
        """
        Registra una clase de acción.

        Args:
            action_class: Clase de acción a registrar
        """
        name = action_class.metadata.name
        cls._actions[name] = action_class
        logger.debug(f"Acción registrada: {name}")

    @classmethod
    def register_decorator(cls, action_type: str):
        """
        Decorador para registrar acciones.

        Usage:
            @ActionRegistry.register_decorator("my_action")
            class MyAction(ActionBase):
                ...
        """
        def decorator(action_class: Type[ActionBase]):
            action_class.metadata.name = action_type
            cls._actions[action_type] = action_class
            return action_class
        return decorator

    @classmethod
    def get(cls, action_type: str) -> Optional[ActionBase]:
        """
        Obtiene una instancia de acción por su tipo.

        Args:
            action_type: Tipo de acción

        Returns:
            Instancia de la acción o None
        """
        action_class = cls._actions.get(action_type)
        if action_class:
            return action_class()
        return None

    @classmethod
    def get_class(cls, action_type: str) -> Optional[Type[ActionBase]]:
        """
        Obtiene la clase de acción por su tipo.

        Args:
            action_type: Tipo de acción

        Returns:
            Clase de acción o None
        """
        return cls._actions.get(action_type)

    @classmethod
    def exists(cls, action_type: str) -> bool:
        """Verifica si una acción existe."""
        return action_type in cls._actions

    @classmethod
    def list_all(cls) -> List[str]:
        """Lista todos los tipos de acciones registradas."""
        return list(cls._actions.keys())

    @classmethod
    def list_by_category(cls, category: ActionCategory) -> List[str]:
        """
        Lista acciones por categoría.

        Args:
            category: Categoría a filtrar

        Returns:
            Lista de nombres de acciones
        """
        return [
            name for name, action_class in cls._actions.items()
            if action_class.metadata.category == category
        ]

    @classmethod
    def get_metadata(cls, action_type: str) -> Optional[ActionMetadata]:
        """
        Obtiene los metadatos de una acción.

        Args:
            action_type: Tipo de acción

        Returns:
            Metadatos o None
        """
        action_class = cls._actions.get(action_type)
        if action_class:
            return action_class.metadata
        return None

    @classmethod
    def generate_actions_prompt(cls, language: str = "es") -> str:
        """
        Genera una descripción de acciones para el prompt del LLM.

        Args:
            language: Idioma de las descripciones

        Returns:
            String con las acciones disponibles
        """
        lines = []

        # Agrupar por categoría
        categories = {}
        for name, action_class in cls._actions.items():
            cat = action_class.metadata.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(action_class.metadata)

        for cat_name, actions in categories.items():
            lines.append(f"\n{cat_name.upper()}:")
            for meta in actions:
                desc = meta.description_en if language == "en" else meta.description
                params = ", ".join(meta.required_params)
                if params:
                    lines.append(f"  - {meta.name}({params}): {desc}")
                else:
                    lines.append(f"  - {meta.name}: {desc}")

        return "\n".join(lines)

    @classmethod
    def search_by_keyword(cls, keyword: str, language: str = "es") -> List[str]:
        """
        Busca acciones por palabra clave.

        Args:
            keyword: Palabra clave a buscar
            language: Idioma de las keywords

        Returns:
            Lista de nombres de acciones que coinciden
        """
        keyword_lower = keyword.lower()
        results = []

        for name, action_class in cls._actions.items():
            meta = action_class.metadata
            keywords = meta.keywords_es if language == "es" else meta.keywords_en

            # Buscar en keywords y descripción
            if any(keyword_lower in kw.lower() for kw in keywords):
                results.append(name)
            elif keyword_lower in meta.description.lower():
                results.append(name)
            elif keyword_lower in meta.description_en.lower():
                results.append(name)

        return results

    @classmethod
    def clear(cls) -> None:
        """Limpia el registro (útil para testing)."""
        cls._actions.clear()
        cls._initialized = False
