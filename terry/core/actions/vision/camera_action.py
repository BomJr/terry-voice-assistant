"""
Camera Action - Terry v6.1
Acción de voz para controlar la cámara y obtener información
"""
from typing import Any, Dict
from terry.core.actions.base import ActionBase, ActionResult
from terry.features.vision.camera import get_camera_vision_manager, start_camera_service, stop_camera_service


class CameraAction(ActionBase):
    """Acción para control de cámara y reconocimiento facial."""

    def __init__(self):
        super().__init__(
            name="camera",
            description="Control de cámara: quién está presente, iniciar/detener servicio",
            description_en="Camera control: who is present, start/stop service"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Ejecutar acción de cámara.

        Parámetros:
        - action: who_is_here, start, stop, status, stats
        - name: nombre de persona (opcional, para is_present)
        """
        action = params.get('action', 'who_is_here')
        manager = get_camera_vision_manager()

        # Iniciar servicio
        if action == 'start':
            if manager._running:
                return ActionResult(
                    success=True,
                    message="El servicio de cámara ya está activo",
                    data={'status': 'already_running'}
                )

            success = start_camera_service()
            if success:
                return ActionResult(
                    success=True,
                    message="Servicio de cámara iniciado correctamente",
                    data={'status': 'started'}
                )
            else:
                return ActionResult(
                    success=False,
                    message="Error al iniciar el servicio de cámara"
                )

        # Detener servicio
        elif action == 'stop':
            if not manager._running:
                return ActionResult(
                    success=True,
                    message="El servicio de cámara no estaba activo"
                )

            stop_camera_service()
            return ActionResult(
                success=True,
                message="Servicio de cámara detenido",
                data={'status': 'stopped'}
            )

        # Verificar si el servicio está activo
        if not manager._running:
            return ActionResult(
                success=False,
                message="El servicio de cámara no está activo. Di 'activa la cámara' para iniciarlo"
            )

        # ¿Quién está aquí?
        if action == 'who_is_here':
            people = manager.who_is_present()

            if not people:
                return ActionResult(
                    success=True,
                    message="No detecto a nadie en este momento",
                    data={'people': [], 'count': 0}
                )

            # Filtrar "Unknown"
            known_people = [p for p in people if p != "Unknown"]

            if len(known_people) == 0:
                unknown_count = len([p for p in people if p == "Unknown"])
                return ActionResult(
                    success=True,
                    message=f"Detecto {unknown_count} persona{'s' if unknown_count > 1 else ''} desconocida{'s' if unknown_count > 1 else ''}",
                    data={'people': people, 'count': len(people), 'known_count': 0}
                )

            elif len(known_people) == 1:
                message = f"Detecto a {known_people[0]}"
            elif len(known_people) == 2:
                message = f"Detecto a {known_people[0]} y {known_people[1]}"
            else:
                message = f"Detecto a {', '.join(known_people[:-1])} y {known_people[-1]}"

            return ActionResult(
                success=True,
                message=message,
                data={'people': people, 'count': len(people), 'known_count': len(known_people)}
            )

        # ¿Está [nombre] presente?
        elif action == 'is_present':
            name = params.get('name', '')

            if not name:
                return ActionResult(
                    success=False,
                    message="Necesito un nombre para verificar presencia"
                )

            is_present = manager.is_person_present(name)

            if is_present:
                return ActionResult(
                    success=True,
                    message=f"Sí, {name} está aquí",
                    data={'name': name, 'present': True}
                )
            else:
                return ActionResult(
                    success=True,
                    message=f"No, {name} no está aquí",
                    data={'name': name, 'present': False}
                )

        # Estado del servicio
        elif action == 'status':
            presence = manager.get_current_presence()

            return ActionResult(
                success=True,
                message=f"Cámara activa. {presence['count']} persona{'s' if presence['count'] != 1 else ''} detectada{'s' if presence['count'] != 1 else ''}",
                data=presence
            )

        # Estadísticas
        elif action == 'stats':
            stats = manager.get_stats()

            uptime_minutes = int(stats['uptime_seconds'] / 60) if stats['uptime_seconds'] else 0

            return ActionResult(
                success=True,
                message=f"Estadísticas: {stats['total_detections']} detecciones, {stats['recognized_count']} reconocidas, activo desde hace {uptime_minutes} minutos",
                data=stats
            )

        else:
            return ActionResult(
                success=False,
                message=f"Acción desconocida: {action}"
            )
