"""
Home-Alexa - Routine Manager
Gestiona y ejecuta rutinas (macros) predefinidas
"""

import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from actions.action_base import ActionBase, ActionMetadata, ActionResult, ActionCategory, RiskLevel
from actions.action_registry import ActionRegistry
from utils.logger import get_logger

logger = get_logger(__name__)


class RoutineManager:
    """Gestor de rutinas predefinidas."""

    def __init__(self, routines_file: Optional[str] = None):
        """
        Inicializa el gestor de rutinas.

        Args:
            routines_file: Ruta al archivo de rutinas YAML (opcional, usa ruta por defecto)
        """
        if routines_file is None:
            # Use absolute path relative to project root
            project_root = Path(__file__).parent.parent.parent
            self.routines_file = project_root / "config" / "routines.yaml"
        else:
            self.routines_file = Path(routines_file)

        self.routines: Dict[str, Dict[str, Any]] = {}
        self.load_routines()

    def load_routines(self):
        """Carga las rutinas desde el archivo YAML."""
        if not self.routines_file.exists():
            logger.warning(f"Archivo de rutinas no encontrado: {self.routines_file}")
            return

        try:
            with open(self.routines_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.routines = data.get('routines', {})
                logger.info(f"Cargadas {len(self.routines)} rutinas")
        except Exception as e:
            logger.error(f"Error cargando rutinas: {e}")

    def get_routine(self, routine_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una rutina por nombre.

        Args:
            routine_name: Nombre de la rutina

        Returns:
            Diccionario con la rutina o None
        """
        return self.routines.get(routine_name)

    def find_routine_by_keyword(self, user_input: str) -> Optional[str]:
        """
        Busca una rutina que coincida con el input del usuario.

        Args:
            user_input: Texto del usuario

        Returns:
            Nombre de la rutina o None
        """
        user_input_lower = user_input.lower().strip()

        for routine_name, routine_data in self.routines.items():
            keywords = routine_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    logger.info(f"Rutina encontrada: {routine_name}")
                    return routine_name

        return None

    async def execute_routine(
        self,
        routine_name: str,
        action_registry: ActionRegistry
    ) -> List[ActionResult]:
        """
        Ejecuta una rutina.

        Args:
            routine_name: Nombre de la rutina
            action_registry: Registro de acciones

        Returns:
            Lista de resultados de cada acción
        """
        routine = self.get_routine(routine_name)
        if not routine:
            logger.error(f"Rutina no encontrada: {routine_name}")
            return [ActionResult(
                success=False,
                message=f"Rutina '{routine_name}' no encontrada",
                data={}
            )]

        actions_data = routine.get('actions', [])
        results = []

        logger.info(f"Ejecutando rutina '{routine_name}' ({len(actions_data)} acciones)")

        for idx, action_data in enumerate(actions_data, 1):
            action_type = action_data.get('type')
            params = action_data.get('params', {})

            logger.debug(f"Acción {idx}/{len(actions_data)}: {action_type}")

            # Obtener la acción del registro
            action = action_registry.get_action(action_type)
            if not action:
                logger.warning(f"Acción no encontrada: {action_type}")
                results.append(ActionResult(
                    success=False,
                    message=f"Acción '{action_type}' no encontrada",
                    data={}
                ))
                continue

            # Ejecutar la acción
            try:
                result = await action.execute(params)
                results.append(result)

                if not result.success:
                    logger.warning(f"Acción {action_type} falló: {result.message}")

                # Pequeña pausa entre acciones
                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"Error ejecutando acción {action_type}: {e}")
                results.append(ActionResult(
                    success=False,
                    message=f"Error: {e}",
                    data={}
                ))

        successful = sum(1 for r in results if r.success)
        logger.info(f"Rutina '{routine_name}' completada: {successful}/{len(results)} exitosas")

        return results

    def list_routines(self) -> List[Dict[str, str]]:
        """
        Lista todas las rutinas disponibles.

        Returns:
            Lista de diccionarios con nombre y descripción
        """
        return [
            {
                "name": name,
                "description": data.get("description", ""),
                "keywords": ", ".join(data.get("keywords", []))
            }
            for name, data in self.routines.items()
        ]

    def print_routines(self):
        """Imprime todas las rutinas disponibles."""
        routines = self.list_routines()

        if not routines:
            print("No hay rutinas disponibles")
            return

        print("\n📋 RUTINAS DISPONIBLES")
        print("=" * 70)
        for routine in routines:
            print(f"  • {routine['name']}")
            print(f"    {routine['description']}")
            print(f"    Comandos: {routine['keywords']}")
            print()
        print("=" * 70)


class RoutineAction(ActionBase):
    """Acción para ejecutar rutinas predefinidas."""

    metadata = ActionMetadata(
        name="routine",
        description="Ejecuta una rutina predefinida",
        description_en="Execute a predefined routine",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["rutina", "modo", "configurar"],
        keywords_en=["routine", "mode", "setup"]
    )

    def __init__(self):
        super().__init__()
        self.routine_manager = RoutineManager()

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Ejecuta una rutina.

        Params esperados:
            routine_name: str - Nombre de la rutina
        """
        routine_name = params.get("routine_name")

        if not routine_name:
            return ActionResult(
                success=False,
                message="Falta el nombre de la rutina",
                data={}
            )

        # Obtener el registro de acciones (debe ser inyectado)
        from actions.action_registry import get_registry
        registry = get_registry()

        results = await self.routine_manager.execute_routine(
            routine_name,
            registry
        )

        successful = sum(1 for r in results if r.success)
        total = len(results)

        return ActionResult(
            success=successful == total,
            message=f"Rutina '{routine_name}' ejecutada: {successful}/{total} acciones exitosas",
            data={
                "routine_name": routine_name,
                "total_actions": total,
                "successful_actions": successful,
                "results": [r.to_dict() for r in results]
            }
        )


# Instancia global
_routine_manager_instance: Optional[RoutineManager] = None


def get_routine_manager() -> RoutineManager:
    """Obtiene la instancia global del gestor de rutinas."""
    global _routine_manager_instance
    if _routine_manager_instance is None:
        _routine_manager_instance = RoutineManager()
    return _routine_manager_instance
