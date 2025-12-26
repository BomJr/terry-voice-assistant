"""
Home-Alexa - Ollama Client
Cliente asíncrono para interactuar con Ollama
"""

import asyncio
import json
from typing import Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass

from terry.core.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx no disponible")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama no disponible, usando httpx directamente")


@dataclass
class LLMResponse:
    """Respuesta del LLM."""
    text: str
    model: str
    total_duration: Optional[float] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class OllamaClient:
    """
    Cliente asíncrono para Ollama.
    Soporta tanto la librería oficial como requests directos.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.1:latest",
        fallback_model: str = "llama3:latest",
        timeout: int = 30,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.fallback_model = fallback_model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client: Optional[httpx.AsyncClient] = None
        self._current_model = model

    async def initialize(self) -> None:
        """Inicializa el cliente."""
        if HTTPX_AVAILABLE:
            self._client = httpx.AsyncClient(timeout=self.timeout)

        # Verificar conexión y modelo
        if await self._check_model(self.model):
            self._current_model = self.model
            logger.info(f"Modelo principal disponible: {self.model}")
        elif await self._check_model(self.fallback_model):
            self._current_model = self.fallback_model
            logger.warning(f"Usando modelo fallback: {self.fallback_model}")
        else:
            logger.error("Ningún modelo disponible en Ollama")

    async def _check_model(self, model: str) -> bool:
        """Verifica si un modelo está disponible."""
        try:
            if OLLAMA_AVAILABLE:
                models = ollama.list()
                return any(m.get('name', '').startswith(model.split(':')[0])
                           for m in models.get('models', []))

            if self._client:
                response = await self._client.get(f"{self.host}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return any(m.get('name', '').startswith(model.split(':')[0])
                               for m in data.get('models', []))
            return False
        except Exception as e:
            logger.debug(f"Error verificando modelo {model}: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Genera una respuesta del LLM.

        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura de generación
            max_tokens: Máximo de tokens a generar

        Returns:
            LLMResponse con el texto generado
        """
        temp = temperature or self.temperature
        max_tok = max_tokens or self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            if OLLAMA_AVAILABLE:
                return await self._generate_with_ollama(messages, temp, max_tok)
            else:
                return await self._generate_with_httpx(messages, temp, max_tok)
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return LLMResponse(text="", model=self._current_model)

    async def _generate_with_ollama(
        self,
        messages: list,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Genera usando la librería oficial de Ollama."""
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: ollama.chat(
                model=self._current_model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
        )

        return LLMResponse(
            text=response['message']['content'],
            model=response.get('model', self._current_model),
            total_duration=response.get('total_duration'),
            prompt_eval_count=response.get('prompt_eval_count'),
            eval_count=response.get('eval_count')
        )

    async def _generate_with_httpx(
        self,
        messages: list,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Genera usando httpx directamente."""
        if not self._client:
            raise RuntimeError("Cliente HTTP no inicializado")

        payload = {
            "model": self._current_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        response = await self._client.post(
            f"{self.host}/api/chat",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return LLMResponse(
            text=data['message']['content'],
            model=data.get('model', self._current_model),
            total_duration=data.get('total_duration'),
            prompt_eval_count=data.get('prompt_eval_count'),
            eval_count=data.get('eval_count')
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        Genera respuesta en streaming.

        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema
            temperature: Temperatura
            max_tokens: Máximo de tokens

        Yields:
            Fragmentos de texto
        """
        if not self._client:
            yield ""
            return

        temp = temperature or self.temperature
        max_tok = max_tokens or self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._current_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temp,
                "num_predict": max_tok,
            }
        }

        try:
            async with self._client.stream(
                "POST",
                f"{self.host}/api/chat",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error en streaming: {e}")

    async def close(self) -> None:
        """Cierra el cliente."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def is_ready(self) -> bool:
        """Verifica si el cliente está listo."""
        return self._current_model is not None

    @property
    def current_model(self) -> str:
        """Modelo actualmente en uso."""
        return self._current_model


async def test_ollama_connection(host: str = "http://localhost:11434") -> bool:
    """Prueba la conexión a Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{host}/api/tags")
            return response.status_code == 200
    except Exception:
        return False
