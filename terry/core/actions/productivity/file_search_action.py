"""
File Search Action - Terry v6.1
Search files using macOS Spotlight
"""
from typing import Any, Dict
from terry.core.actions.base import ActionBase, ActionResult
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class FileSearchAction(ActionBase):
    """File search action using Spotlight."""

    def __init__(self):
        super().__init__(
            name="file_search",
            description="Buscar archivos en el sistema",
            description_en="Search files in the system"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute file search action.

        Args:
            params: Action parameters
                - action: 'search', 'search_content', 'open'
                - query: Search query
                - file_type: File extension filter
                - directory: Directory to search in
                - file_path: File path to open

        Returns:
            ActionResult with search results
        """
        try:
            from terry.features.productivity.file_search import get_file_search
            search = get_file_search()

            action = params.get('action', 'search')

            if action == 'search':
                # Search for files by name
                query = params.get('query')
                file_type = params.get('file_type')
                directory = params.get('directory')

                if not query:
                    return ActionResult(
                        success=False,
                        message="Necesito un término de búsqueda"
                    )

                results = search.search(
                    query=query,
                    file_type=file_type,
                    directory=directory
                )

                if results:
                    # Format results for voice response
                    file_names = [r['name'] for r in results[:3]]  # First 3
                    message = f"Encontré {len(results)} archivos:\n" + "\n".join([f"• {name}" for name in file_names])

                    return ActionResult(
                        success=True,
                        message=message,
                        data={
                            'results': results,
                            'count': len(results),
                            'query': query
                        }
                    )
                else:
                    return ActionResult(
                        success=True,
                        message=f"No encontré archivos con '{query}'"
                    )

            elif action == 'search_content':
                # Search file contents
                query = params.get('query')
                directory = params.get('directory')

                if not query:
                    return ActionResult(
                        success=False,
                        message="Necesito un término de búsqueda"
                    )

                results = search.search_by_content(
                    query=query,
                    directory=directory
                )

                if results:
                    file_names = [r['name'] for r in results[:3]]
                    message = f"Encontré {len(results)} archivos con '{query}':\n" + "\n".join([f"• {name}" for name in file_names])

                    return ActionResult(
                        success=True,
                        message=message,
                        data={
                            'results': results,
                            'count': len(results),
                            'query': query
                        }
                    )
                else:
                    return ActionResult(
                        success=True,
                        message=f"No encontré archivos que contengan '{query}'"
                    )

            elif action == 'open':
                # Open a file
                file_path = params.get('file_path')

                if not file_path:
                    return ActionResult(
                        success=False,
                        message="Necesito la ruta del archivo"
                    )

                success = search.open_file(file_path)

                if success:
                    return ActionResult(
                        success=True,
                        message=f"Abriendo archivo"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude abrir el archivo"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción de búsqueda no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="File search no está disponible. Revisa la configuración"
            )
        except Exception as e:
            logger.error(f"Error in file search: {e}")
            return ActionResult(
                success=False,
                message=f"Error en búsqueda: {str(e)}"
            )
