"""
Home-Alexa - Permissions Checker
Verifica que todos los permisos necesarios estén otorgados
"""

import subprocess
import sys
from typing import List, Tuple, Dict
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class PermissionsChecker:
    """Verifica permisos del sistema necesarios para Home-Alexa."""

    @staticmethod
    def check_accessibility_permissions() -> Tuple[bool, str]:
        """
        Verifica si Terminal tiene permisos de Accesibilidad.

        Returns:
            (tiene_permisos, mensaje)
        """
        try:
            # Intentar ejecutar un comando que requiere permisos
            script = '''
                tell application "System Events"
                    return true
                end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, "✅ Permisos de Accesibilidad: OK"
            else:
                error_msg = result.stderr.lower()
                if "not allowed" in error_msg or "assistive" in error_msg:
                    return False, "❌ Terminal necesita permisos de Accesibilidad"
                return True, "✅ Permisos de Accesibilidad: OK"

        except subprocess.TimeoutExpired:
            return False, "⚠️  Timeout verificando permisos"
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return False, f"⚠️  Error verificando permisos: {e}"

    @staticmethod
    def check_ollama_running() -> Tuple[bool, str]:
        """
        Verifica si Ollama está corriendo.

        Returns:
            (está_corriendo, mensaje)
        """
        try:
            import requests
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                return True, "✅ Ollama: Corriendo"
            return False, "❌ Ollama no responde correctamente"
        except requests.exceptions.ConnectionError:
            return False, "❌ Ollama no está corriendo"
        except Exception as e:
            return False, f"⚠️  Error verificando Ollama: {e}"

    @staticmethod
    def check_ollama_model(model_name: str = "llama3.1:latest") -> Tuple[bool, str]:
        """
        Verifica si el modelo de Ollama está instalado.

        Returns:
            (está_instalado, mensaje)
        """
        try:
            import requests
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                if model_name in models:
                    return True, f"✅ Modelo {model_name}: Instalado"
                return False, f"❌ Modelo {model_name} no encontrado"
            return False, "⚠️  No se pudo verificar modelos"
        except Exception as e:
            return False, f"⚠️  Error verificando modelo: {e}"

    @staticmethod
    def check_nowplaying_cli() -> Tuple[bool, str]:
        """
        Verifica si nowplaying-cli está instalado.

        Returns:
            (está_instalado, mensaje)
        """
        try:
            result = subprocess.run(
                ['which', 'nowplaying-cli'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return True, "✅ nowplaying-cli: Instalado"
            return False, "⚠️  nowplaying-cli no instalado (opcional)"
        except Exception as e:
            return False, f"⚠️  Error verificando nowplaying-cli: {e}"

    @staticmethod
    def check_python_version() -> Tuple[bool, str]:
        """
        Verifica la versión de Python.

        Returns:
            (versión_ok, mensaje)
        """
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major == 3 and version.minor >= 10:
            return True, f"✅ Python {version_str}: OK"
        return False, f"⚠️  Python {version_str}: Se recomienda 3.10+"

    @classmethod
    def check_all(cls, verbose: bool = True) -> Dict[str, Tuple[bool, str]]:
        """
        Verifica todos los requisitos del sistema.

        Args:
            verbose: Si es True, imprime los resultados

        Returns:
            Diccionario con resultados de cada verificación
        """
        checks = {
            "python": cls.check_python_version(),
            "accessibility": cls.check_accessibility_permissions(),
            "ollama": cls.check_ollama_running(),
            "ollama_model": cls.check_ollama_model(),
            "nowplaying": cls.check_nowplaying_cli(),
        }

        if verbose:
            print("\n🔍 VERIFICACIÓN DEL SISTEMA")
            print("=" * 50)
            for name, (success, message) in checks.items():
                print(f"  {message}")
            print("=" * 50)

        return checks

    @classmethod
    def are_critical_requirements_met(cls) -> bool:
        """
        Verifica si los requisitos críticos están cumplidos.

        Returns:
            True si todos los requisitos críticos están OK
        """
        checks = cls.check_all(verbose=False)

        # Requisitos críticos
        critical = ["python", "accessibility", "ollama", "ollama_model"]

        return all(checks[req][0] for req in critical)

    @classmethod
    def get_installation_instructions(cls) -> str:
        """
        Retorna instrucciones de instalación para requisitos faltantes.

        Returns:
            String con instrucciones
        """
        checks = cls.check_all(verbose=False)
        instructions = []

        if not checks["accessibility"][0]:
            instructions.append("""
📋 PERMISOS DE ACCESIBILIDAD:
   1. Abre Preferencias del Sistema
   2. Ve a Privacidad y Seguridad → Accesibilidad
   3. Activa el checkbox para Terminal
   4. Reinicia esta aplicación
""")

        if not checks["ollama"][0]:
            instructions.append("""
📋 OLLAMA NO ESTÁ CORRIENDO:
   Ejecuta en otra terminal:
   $ ollama serve
""")

        if not checks["ollama_model"][0]:
            instructions.append("""
📋 MODELO OLLAMA NO INSTALADO:
   Ejecuta:
   $ ollama pull llama3.1:latest
""")

        if not checks["nowplaying"][0]:
            instructions.append("""
📋 NOWPLAYING-CLI (OPCIONAL):
   Para mejor control de música, instala:
   $ ./install_nowplaying.sh
   o
   $ brew install nowplaying-cli
""")

        return "\n".join(instructions) if instructions else "✅ Todos los requisitos están cumplidos"


def main():
    """Función principal para ejecutar desde línea de comandos."""
    checker = PermissionsChecker()
    checks = checker.check_all(verbose=True)

    print()
    if checker.are_critical_requirements_met():
        print("✅ SISTEMA LISTO PARA USAR")
        print()
    else:
        print("❌ FALTAN REQUISITOS CRÍTICOS")
        print()
        print(checker.get_installation_instructions())
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
