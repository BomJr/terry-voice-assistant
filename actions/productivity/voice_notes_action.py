"""
Voice Notes Action - Terry v6.1
Manage voice notes: create, search, list, complete, delete
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult, ActionCategory
from notes.voice_notes import get_notes_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceNotesAction(ActionBase):
    """Action for managing voice notes."""

    def __init__(self):
        """Initialize Voice Notes Action."""
        super().__init__(
            name="voice_notes",
            description="Gestionar notas por voz: crear, buscar, listar, completar",
            description_en="Manage voice notes: create, search, list, complete",
            category=ActionCategory.PRODUCTIVITY
        )

        # Set metadata
        self.metadata.required_params = []  # All params are optional, action type determines behavior
        self.metadata.keywords_es = [
            "nota", "notas", "recordar", "apuntar", "buscar notas",
            "mis notas", "pendientes", "lista", "completar nota"
        ]
        self.metadata.keywords_en = [
            "note", "notes", "remember", "write down", "search notes",
            "my notes", "pending", "list", "complete note"
        ]

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute the voice notes action.

        Args:
            params: Action parameters
                - action: 'add', 'search', 'list', 'complete', 'delete', 'get'
                - content: Note content (for add)
                - query: Search query (for search)
                - note_id: Note ID (for complete/delete/get)
                - category: Category filter (optional)
                - priority: Priority level 0-2 (for add)

        Returns:
            ActionResult with success status and message
        """
        notes_mgr = get_notes_manager()
        action = params.get('action', 'add').lower()

        try:
            # ADD NOTE
            if action == 'add':
                content = params.get('content')
                if not content:
                    return ActionResult(
                        success=False,
                        message="No se proporcionó contenido para la nota"
                    )

                category = params.get('category', 'general')
                tags = params.get('tags', [])
                priority = params.get('priority', 0)

                note_id = notes_mgr.add_note(
                    content=content,
                    category=category,
                    tags=tags,
                    priority=priority
                )

                priority_text = {0: "", 1: " (alta prioridad)", 2: " (urgente)"}
                return ActionResult(
                    success=True,
                    message=f"Nota guardada{priority_text.get(priority, '')}: {content[:50]}...",
                    data={'note_id': note_id, 'content': content, 'category': category}
                )

            # SEARCH NOTES
            elif action == 'search':
                query = params.get('query')
                if not query:
                    return ActionResult(
                        success=False,
                        message="No se proporcionó consulta de búsqueda"
                    )

                category = params.get('category')
                limit = params.get('limit', 5)

                results = notes_mgr.search_notes(query, limit=limit, category=category)

                if results:
                    # Format results
                    messages = []
                    for i, note in enumerate(results[:3], 1):  # Show top 3
                        priority_mark = {0: "", 1: " ⚠️", 2: " 🚨"}
                        category_text = f" [{note['category']}]" if note['category'] != 'general' else ""
                        messages.append(
                            f"{i}. {note['content'][:60]}{priority_mark.get(note['priority'], '')}{category_text}"
                        )

                    result_msg = f"Encontré {len(results)} nota{'s' if len(results) > 1 else ''}:\n" + "\n".join(messages)

                    return ActionResult(
                        success=True,
                        message=result_msg,
                        data={'notes': results, 'count': len(results)}
                    )
                else:
                    return ActionResult(
                        success=True,
                        message=f"No encontré notas sobre '{query}'"
                    )

            # LIST NOTES
            elif action in ['list', 'show', 'recent']:
                category = params.get('category')
                limit = params.get('limit', 10)
                include_completed = params.get('include_completed', False)

                notes = notes_mgr.get_recent_notes(
                    limit=limit,
                    category=category,
                    include_completed=include_completed
                )

                if notes:
                    # Format results
                    messages = []
                    for i, note in enumerate(notes[:5], 1):  # Show top 5
                        priority_mark = {0: "", 1: " ⚠️", 2: " 🚨"}
                        category_text = f" [{note['category']}]" if note['category'] != 'general' else ""
                        completed_mark = " ✓" if note['completed'] else ""
                        messages.append(
                            f"{i}. {note['content'][:60]}{priority_mark.get(note['priority'], '')}{category_text}{completed_mark}"
                        )

                    category_text = f" de {category}" if category else ""
                    result_msg = f"Tus últimas notas{category_text}:\n" + "\n".join(messages)

                    return ActionResult(
                        success=True,
                        message=result_msg,
                        data={'notes': notes, 'count': len(notes)}
                    )
                else:
                    category_text = f" en {category}" if category else ""
                    return ActionResult(
                        success=True,
                        message=f"No tienes notas{category_text}"
                    )

            # COMPLETE NOTE
            elif action in ['complete', 'done', 'finish']:
                note_id = params.get('note_id')
                if not note_id:
                    # Try to complete most recent note
                    recent = notes_mgr.get_recent_notes(limit=1)
                    if recent:
                        note_id = recent[0]['id']
                    else:
                        return ActionResult(
                            success=False,
                            message="No hay notas para completar"
                        )

                note = notes_mgr.get_note_by_id(note_id)
                if note:
                    notes_mgr.mark_completed(note_id)
                    return ActionResult(
                        success=True,
                        message=f"Nota completada: {note['content'][:50]}...",
                        data={'note_id': note_id}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message=f"No encontré la nota {note_id}"
                    )

            # DELETE NOTE
            elif action == 'delete':
                note_id = params.get('note_id')
                if not note_id:
                    return ActionResult(
                        success=False,
                        message="Se requiere ID de nota para eliminar"
                    )

                note = notes_mgr.get_note_by_id(note_id)
                if note:
                    notes_mgr.delete_note(note_id)
                    return ActionResult(
                        success=True,
                        message=f"Nota eliminada: {note['content'][:50]}...",
                        data={'note_id': note_id}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message=f"No encontré la nota {note_id}"
                    )

            # GET CATEGORIES
            elif action == 'categories':
                categories = notes_mgr.get_categories()
                if categories:
                    return ActionResult(
                        success=True,
                        message=f"Categorías: {', '.join(categories)}",
                        data={'categories': categories}
                    )
                else:
                    return ActionResult(
                        success=True,
                        message="No hay categorías aún"
                    )

            # UNKNOWN ACTION
            else:
                return ActionResult(
                    success=False,
                    message=f"Acción desconocida: {action}. Usa: add, search, list, complete, delete"
                )

        except Exception as e:
            logger.error(f"Error in voice notes action: {e}", exc_info=True)
            return ActionResult(
                success=False,
                message=f"Error gestionando notas: {str(e)}"
            )
