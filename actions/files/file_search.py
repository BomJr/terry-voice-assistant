"""
Home-Alexa - File Search Actions
Búsqueda de archivos usando Spotlight (mdfind)
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from actions.action_base import ActionBase, ActionMetadata, ActionResult, ActionCategory, RiskLevel
from utils.logger import get_logger

logger = get_logger(__name__)


class FileSearchAction(ActionBase):
    """Busca archivos usando Spotlight."""

    metadata = ActionMetadata(
        name="file_search",
        description="Busca archivos en el sistema",
        category=ActionCategory.FILE,
        risk_level=RiskLevel.SAFE,
        keywords_es=["buscar", "encontrar", "archivo", "documento"],
        keywords_en=["search", "find", "file", "document"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Busca archivos usando mdfind.

        Params esperados:
            query: str - Término de búsqueda
            file_type: str (opcional) - Tipo de archivo (pdf, doc, jpg, etc.)
            limit: int (opcional) - Máximo de resultados (default: 10)
        """
        query = params.get("query", "")
        file_type = params.get("file_type")
        limit = params.get("limit", 10)

        if not query:
            return ActionResult(
                success=False,
                message="Falta el término de búsqueda",
                data={}
            )

        try:
            # Construir comando mdfind
            cmd = ['mdfind']

            # Agregar filtro de tipo de archivo si se especifica
            if file_type:
                # kMDItemContentType para filtrar por tipo
                cmd.extend(['-onlyin', str(Path.home())])
                search_query = f'kMDItemDisplayName == "*{query}*" && kMDItemKind == "*{file_type}*"'
            else:
                search_query = query

            cmd.append(search_query)

            # Ejecutar búsqueda
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Procesar resultados
                files = result.stdout.strip().split('\n')
                files = [f for f in files if f]  # Filtrar líneas vacías

                # Limitar resultados
                files = files[:limit]

                if not files:
                    return ActionResult(
                        success=True,
                        message=f"No se encontraron archivos con '{query}'",
                        data={"query": query, "results": []}
                    )

                return ActionResult(
                    success=True,
                    message=f"Encontrados {len(files)} archivos",
                    data={
                        "query": query,
                        "count": len(files),
                        "results": files
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error en búsqueda: {result.stderr}",
                    data={}
                )

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                message="Búsqueda excedió el tiempo límite",
                data={}
            )
        except Exception as e:
            logger.error(f"Error en búsqueda de archivos: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class FileOpenAction(ActionBase):
    """Abre un archivo."""

    metadata = ActionMetadata(
        name="file_open",
        description="Abre un archivo",
        category=ActionCategory.FILE,
        risk_level=RiskLevel.SAFE,
        keywords_es=["abrir", "archivo", "documento"],
        keywords_en=["open", "file", "document"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Abre un archivo.

        Params esperados:
            path: str - Ruta del archivo
        """
        file_path = params.get("path", "")

        if not file_path:
            return ActionResult(
                success=False,
                message="Falta la ruta del archivo",
                data={}
            )

        try:
            # Expandir ~ y verificar que existe
            full_path = os.path.expanduser(file_path)

            if not os.path.exists(full_path):
                return ActionResult(
                    success=False,
                    message=f"Archivo no encontrado: {file_path}",
                    data={}
                )

            # Abrir con la aplicación predeterminada
            subprocess.run(
                ['open', full_path],
                check=True,
                timeout=5
            )

            return ActionResult(
                success=True,
                message=f"Abriendo {os.path.basename(full_path)}",
                data={"path": full_path}
            )

        except subprocess.CalledProcessError as e:
            return ActionResult(
                success=False,
                message=f"Error abriendo archivo: {e}",
                data={}
            )
        except Exception as e:
            logger.error(f"Error en file_open: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class RecentFilesAction(ActionBase):
    """Muestra archivos recientes."""

    metadata = ActionMetadata(
        name="recent_files",
        description="Muestra archivos modificados recientemente",
        category=ActionCategory.FILE,
        risk_level=RiskLevel.SAFE,
        keywords_es=["archivos recientes", "últimos archivos"],
        keywords_en=["recent files", "latest files"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Muestra archivos recientes.

        Params esperados:
            limit: int (opcional) - Máximo de archivos (default: 10)
            days: int (opcional) - Días atrás (default: 7)
        """
        limit = params.get("limit", 10)
        days = params.get("days", 7)

        try:
            # mdfind con fecha de modificación
            # kMDItemFSContentChangeDate >= $time.today(-7)
            query = f'kMDItemFSContentChangeDate >= $time.today(-{days})'

            result = subprocess.run(
                ['mdfind', '-onlyin', str(Path.home()), query],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                files = [f for f in files if f and os.path.isfile(f)]

                # Ordenar por fecha de modificación (más reciente primero)
                files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

                # Limitar resultados
                files = files[:limit]

                if not files:
                    return ActionResult(
                        success=True,
                        message=f"No hay archivos modificados en los últimos {days} días",
                        data={"results": []}
                    )

                # Formatear resultados con fecha
                formatted_files = []
                for file_path in files:
                    mtime = os.path.getmtime(file_path)
                    import datetime
                    date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                    formatted_files.append({
                        "path": file_path,
                        "name": os.path.basename(file_path),
                        "modified": date_str
                    })

                return ActionResult(
                    success=True,
                    message=f"Encontrados {len(files)} archivos recientes",
                    data={
                        "count": len(files),
                        "results": formatted_files
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en recent_files: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class DownloadsAction(ActionBase):
    """Muestra archivos en Downloads."""

    metadata = ActionMetadata(
        name="show_downloads",
        description="Muestra archivos descargados recientemente",
        category=ActionCategory.FILE,
        risk_level=RiskLevel.SAFE,
        keywords_es=["descargas", "downloads", "descargados"],
        keywords_en=["downloads", "downloaded"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Muestra archivos en Downloads.

        Params esperados:
            limit: int (opcional) - Máximo de archivos (default: 10)
        """
        limit = params.get("limit", 10)

        try:
            downloads_dir = Path.home() / "Downloads"

            if not downloads_dir.exists():
                return ActionResult(
                    success=False,
                    message="Carpeta Downloads no encontrada",
                    data={}
                )

            # Listar archivos (no carpetas)
            files = [f for f in downloads_dir.iterdir() if f.is_file()]

            # Ordenar por fecha de modificación
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Limitar
            files = files[:limit]

            if not files:
                return ActionResult(
                    success=True,
                    message="No hay archivos en Downloads",
                    data={"results": []}
                )

            # Formatear resultados
            formatted_files = []
            for file_path in files:
                import datetime
                mtime = file_path.stat().st_mtime
                date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                size_mb = file_path.stat().st_size / (1024 * 1024)

                formatted_files.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "modified": date_str,
                    "size_mb": f"{size_mb:.2f} MB"
                })

            return ActionResult(
                success=True,
                message=f"{len(files)} archivos en Downloads",
                data={
                    "count": len(files),
                    "results": formatted_files
                }
            )

        except Exception as e:
            logger.error(f"Error en show_downloads: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )
