"""
Home-Alexa - Browser Control Actions
Acciones para control del navegador
"""

import subprocess
from typing import Dict, Any
from urllib.parse import quote_plus

from terry.core.actions.base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from terry.core.utils.applescript_runner import run_applescript_sync, AppleScripts
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)

# Navegador por defecto (se puede configurar)
DEFAULT_BROWSER = "Atlas"
FALLBACK_BROWSER = "Google Chrome"


def get_browser(params: Dict[str, Any]) -> str:
    """Obtiene el navegador a usar."""
    return params.get("browser", DEFAULT_BROWSER)


class BrowserOpenUrlAction(ActionBase):
    """Abre una URL en el navegador."""

    metadata = ActionMetadata(
        name="browser_open_url",
        description="Abre una URL en el navegador",
        description_en="Opens a URL in the browser",
        category=ActionCategory.BROWSER,
        risk_level=RiskLevel.SAFE,
        keywords_es=["url", "enlace", "link", "página", "web", "ir"],
        keywords_en=["url", "link", "page", "web", "go", "visit"],
        required_params=["url"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        url = params.get("url", "")
        browser = get_browser(params)

        if not url:
            return ActionResult(
                success=False,
                message="No se especificó la URL",
                error="MISSING_URL"
            )

        # Asegurar que la URL tenga protocolo
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        script = AppleScripts.open_url(url, browser)
        success, output, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"URL abierta en {browser}",
                data={"url": url, "browser": browser}
            )
        else:
            # Intentar con navegador de respaldo
            script = AppleScripts.open_url(url, FALLBACK_BROWSER)
            success, _, error2 = run_applescript_sync(script)

            if success:
                return ActionResult(
                    success=True,
                    message=f"URL abierta en {FALLBACK_BROWSER}",
                    data={"url": url, "browser": FALLBACK_BROWSER}
                )

            return ActionResult(
                success=False,
                message="Error abriendo URL",
                error=error or error2
            )


class BrowserSearchAction(ActionBase):
    """Realiza una búsqueda web."""

    metadata = ActionMetadata(
        name="browser_search",
        description="Busca en la web",
        description_en="Searches the web",
        category=ActionCategory.BROWSER,
        risk_level=RiskLevel.SAFE,
        keywords_es=["buscar", "búsqueda", "google", "search"],
        keywords_en=["search", "google", "find", "look up"],
        required_params=["query"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        query = params.get("query", "")
        browser = get_browser(params)

        if not query:
            return ActionResult(
                success=False,
                message="No se especificó la búsqueda",
                error="MISSING_QUERY"
            )

        # Construir URL de búsqueda
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"

        script = AppleScripts.open_url(search_url, browser)
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"Buscando: {query}",
                data={"query": query, "browser": browser}
            )
        else:
            # Intentar con navegador de respaldo
            script = AppleScripts.open_url(search_url, FALLBACK_BROWSER)
            success, _, error2 = run_applescript_sync(script)

            if success:
                return ActionResult(
                    success=True,
                    message=f"Buscando: {query}",
                    data={"query": query, "browser": FALLBACK_BROWSER}
                )

            return ActionResult(
                success=False,
                message="Error realizando búsqueda",
                error=error or error2
            )


class BrowserNewTabAction(ActionBase):
    """Abre una nueva pestaña en el navegador."""

    metadata = ActionMetadata(
        name="browser_new_tab",
        description="Abre una nueva pestaña",
        description_en="Opens a new tab",
        category=ActionCategory.BROWSER,
        risk_level=RiskLevel.SAFE,
        keywords_es=["nueva", "pestaña", "tab"],
        keywords_en=["new", "tab"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        browser = get_browser(params)

        script = AppleScripts.new_browser_tab(browser)
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message="Nueva pestaña abierta",
                data={"browser": browser}
            )
        else:
            return ActionResult(
                success=False,
                message="Error abriendo nueva pestaña",
                error=error
            )


class BrowserCloseTabAction(ActionBase):
    """Cierra la pestaña actual."""

    metadata = ActionMetadata(
        name="browser_close_tab",
        description="Cierra la pestaña actual",
        description_en="Closes the current tab",
        category=ActionCategory.BROWSER,
        risk_level=RiskLevel.SAFE,
        keywords_es=["cerrar", "pestaña", "tab"],
        keywords_en=["close", "tab"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        browser = get_browser(params)

        script = AppleScripts.close_browser_tab(browser)
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message="Pestaña cerrada",
                data={"browser": browser}
            )
        else:
            return ActionResult(
                success=False,
                message="Error cerrando pestaña",
                error=error
            )
