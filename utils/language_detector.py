"""
Terry - Language Detector
Detección automática de idioma de comandos de voz (v6.0)
"""

from typing import Set


class LanguageDetector:
    """
    Detector simple de idioma basado en keywords.

    Soporta español e inglés.
    """

    # Keywords comunes en inglés
    ENGLISH_KEYWORDS: Set[str] = {
        "play", "pause", "next", "previous", "stop",
        "open", "close", "search", "volume", "louder", "quieter",
        "what", "how", "when", "where", "who", "why",
        "the", "is", "are", "was", "were", "be", "been",
        "hello", "hi", "bye", "thanks", "thank", "please",
        "music", "song", "weather", "time"
    }

    # Keywords comunes en español
    SPANISH_KEYWORDS: Set[str] = {
        "pon", "reproduce", "para", "pausa", "siguiente", "anterior", "detén",
        "abre", "cierra", "busca", "volumen", "más", "menos",
        "qué", "cómo", "cuándo", "dónde", "quién", "por", "porque",
        "el", "la", "los", "las", "un", "una", "es", "son", "está",
        "hola", "adiós", "gracias", "por favor",
        "música", "canción", "tiempo", "clima", "hora"
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detecta el idioma de un texto.

        Args:
            text: Texto a analizar

        Returns:
            'es' para español, 'en' para inglés
        """
        if not text:
            return "es"  # Default español

        text_lower = text.lower()
        words = set(text_lower.split())

        # Contar coincidencias en cada idioma
        en_matches = len(words & cls.ENGLISH_KEYWORDS)
        es_matches = len(words & cls.SPANISH_KEYWORDS)

        # Si hay más coincidencias en inglés, es inglés
        if en_matches > es_matches:
            return "en"

        # Por defecto, español
        return "es"

    @classmethod
    def is_bilingual_command(cls, text: str) -> bool:
        """
        Detecta si un comando mezcla idiomas.

        Args:
            text: Texto a analizar

        Returns:
            True si mezcla español e inglés
        """
        text_lower = text.lower()
        words = set(text_lower.split())

        en_matches = len(words & cls.ENGLISH_KEYWORDS)
        es_matches = len(words & cls.SPANISH_KEYWORDS)

        # Si tiene keywords de ambos idiomas, es bilingüe
        return en_matches > 0 and es_matches > 0


# Función helper global
def detect_language(text: str) -> str:
    """
    Detecta el idioma de un texto.

    Args:
        text: Texto a analizar

    Returns:
        'es' para español, 'en' para inglés
    """
    return LanguageDetector.detect_language(text)
