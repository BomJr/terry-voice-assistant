"""
Home-Alexa - Fuzzy Matcher
Tolerancia a faltas de ortografía y variaciones
"""

import re
from difflib import SequenceMatcher
from typing import Optional, Dict, Any, Tuple


class FuzzyMatcher:
    """Tolerancia a faltas de ortografía y variaciones."""

    # Correcciones comunes de ortografía
    COMMON_TYPOS = {
        # Música/media
        "musica": "música",
        "video": "vídeo",
        "cancion": "canción",
        "canciones": "canciones",
        "proxima": "próxima",
        "proximo": "próximo",
        "continua": "continúa",
        "reanuda": "reanuda",

        # Acciones
        "pon": "pon",
        "pone": "pon",
        "ponme": "pon",
        "reproduce": "reproduce",
        "reporduce": "reproduce",
        "reproduse": "reproduce",
        "reprodu": "reproduce",

        # Comandos comunes con tildes
        "para": "para",
        "detén": "detén",
        "deten": "detén",
        "siguiente": "siguiente",
        "siquiente": "siguiente",
        "siguente": "siguiente",
        "anterior": "anterior",
        "anteror": "anterior",

        # Abrir/cerrar
        "abre": "abre",
        "habr": "abre",
        "habre": "abre",
        "cierra": "cierra",
        "cierra": "cierra",

        # Volumen
        "volumen": "volumen",
        "bolumen": "volumen",
        "volumén": "volumen",
        "sube": "sube",
        "baja": "baja",
        "vaja": "baja",

        # Apps comunes
        "safari": "safari",
        "safary": "safari",
        "safári": "safari",
        "chrome": "chrome",
        "crome": "chrome",
        "spotify": "spotify",
        "spotifi": "spotify",
        "spotfy": "spotify",
        "youtube": "youtube",
        "youtub": "youtube",
        "tu tube": "youtube",
        "utube": "youtube",

        # Rutinas
        "rutina": "rutina",
        "rutína": "rutina",
        "rotina": "rutina",
        "modo": "modo",
        "mañana": "mañana",
        "manana": "mañana",
        "trabajo": "trabajo",
        "travajo": "trabajo",
        "estudio": "estudio",
        "estudió": "estudio",
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normaliza el texto corrigiendo errores comunes.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado
        """
        text = text.lower().strip()

        # Aplicar correcciones comunes palabra por palabra
        words = text.split()
        corrected_words = []

        for word in words:
            # Quitar puntuación
            clean_word = re.sub(r'[^\w\s]', '', word)

            # Buscar corrección
            if clean_word in cls.COMMON_TYPOS:
                corrected_words.append(cls.COMMON_TYPOS[clean_word])
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    @classmethod
    def similarity(cls, str1: str, str2: str) -> float:
        """
        Calcula similitud entre dos strings (0.0 a 1.0).

        Args:
            str1: Primera string
            str2: Segunda string

        Returns:
            Valor de similitud (0.0 = nada similar, 1.0 = idéntico)
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    @classmethod
    def fuzzy_match_pattern(
        cls,
        user_input: str,
        patterns: Dict[str, Any],
        threshold: float = 0.75
    ) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """
        Encuentra el patrón más similar al input del usuario.

        Args:
            user_input: Input del usuario
            patterns: Diccionario de patrones → respuestas
            threshold: Umbral mínimo de similitud (0.0 a 1.0)

        Returns:
            (pattern_matched, response_data, similarity_score) o None
        """
        # Normalizar input
        normalized_input = cls.normalize_text(user_input)

        best_match = None
        best_score = 0.0
        best_pattern = None

        for pattern_key, response_data in patterns.items():
            # Para cada patrón, calcular similitud
            # Convertir pattern regex a texto simple para comparación
            pattern_text = pattern_key

            # Quitar caracteres de regex para texto limpio
            pattern_clean = re.sub(r'[\\^$.*+?{}[\]|()?:]', ' ', pattern_text)
            pattern_clean = ' '.join(pattern_clean.split())

            # Calcular similitud
            score = cls.similarity(normalized_input, pattern_clean)

            if score > best_score and score >= threshold:
                best_score = score
                best_match = response_data
                best_pattern = pattern_key

        if best_match:
            return (best_pattern, best_match, best_score)

        return None

    @classmethod
    def suggest_correction(
        cls,
        user_input: str,
        valid_commands: list,
        max_suggestions: int = 3
    ) -> list:
        """
        Sugiere correcciones para un comando no reconocido.

        Args:
            user_input: Input del usuario
            valid_commands: Lista de comandos válidos
            max_suggestions: Máximo número de sugerencias

        Returns:
            Lista de sugerencias ordenadas por similitud
        """
        suggestions = []

        for command in valid_commands:
            score = cls.similarity(user_input, command)
            if score > 0.5:  # Solo sugerencias razonables
                suggestions.append((command, score))

        # Ordenar por score descendente
        suggestions.sort(key=lambda x: x[1], reverse=True)

        # Retornar solo los comandos (sin scores)
        return [cmd for cmd, score in suggestions[:max_suggestions]]


# Instancia global
_fuzzy_matcher = FuzzyMatcher()


def get_fuzzy_matcher() -> FuzzyMatcher:
    """Obtiene la instancia global."""
    return _fuzzy_matcher
