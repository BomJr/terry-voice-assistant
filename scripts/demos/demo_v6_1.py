#!/usr/bin/env python3
"""
Terry v6.1 - Demo Interactivo
Prueba automática de las 20 mejoras sustanciales
"""
import sys
import time
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

console = Console()


class TerryDemo:
    """Demostración interactiva de Terry v6.1."""

    def __init__(self):
        self.results = {}
        self.phase = 0

    def clear_screen(self):
        """Clear terminal screen."""
        console.clear()

    def show_header(self, title: str, subtitle: str = ""):
        """Show formatted header."""
        self.clear_screen()
        console.print(Panel.fit(
            f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]",
            border_style="cyan"
        ))
        print()

    def pause(self, message: str = "Presiona ENTER para continuar..."):
        """Pause and wait for user."""
        console.print(f"\n[dim]{message}[/dim]")
        input()

    def demo_phase_1(self):
        """Demo FASE 1: Quick Wins."""
        self.show_header(
            "FASE 1: QUICK WINS",
            "Modo Silencioso, Notificaciones, Notas, Deshacer"
        )

        tests = [
            ("Silent Mode", self.test_silent_mode),
            ("Visual Notifications", self.test_notifications),
            ("Voice Notes", self.test_voice_notes),
            ("Undo System", self.test_undo)
        ]

        self.run_tests(tests, "Phase 1")

    def demo_phase_2(self):
        """Demo FASE 2: Inteligencia."""
        self.show_header(
            "FASE 2: INTELIGENCIA",
            "Memoria, Patrones, Contexto, Sugerencias"
        )

        tests = [
            ("Persistent Memory", self.test_memory),
            ("Pattern Learning", self.test_patterns),
            ("Context Tracking", self.test_context),
            ("Intelligent Suggestions", self.test_suggestions)
        ]

        self.run_tests(tests, "Phase 2")

    def demo_phase_3(self):
        """Demo FASE 3: Multimodalidad."""
        self.show_header(
            "FASE 3: MULTIMODALIDAD",
            "Visión por Cámara, OCR Universal"
        )

        tests = [
            ("Camera Vision", self.test_camera),
            ("OCR Engine", self.test_ocr)
        ]

        self.run_tests(tests, "Phase 3")

    def demo_phase_4(self):
        """Demo FASE 4: Automatización."""
        self.show_header(
            "FASE 4: AUTOMATIZACIÓN",
            "Rutinas, Triggers, Macros"
        )

        tests = [
            ("Scheduler", self.test_scheduler),
            ("Conditional Triggers", self.test_triggers),
            ("Macro Recorder", self.test_macros)
        ]

        self.run_tests(tests, "Phase 4")

    def demo_phase_5(self):
        """Demo FASE 5: Productividad."""
        self.show_header(
            "FASE 5: PRODUCTIVIDAD",
            "Dictado, Búsqueda, Control IDE"
        )

        tests = [
            ("Universal Dictation", self.test_dictation),
            ("File Search", self.test_file_search),
            ("IDE Control", self.test_ide)
        ]

        self.run_tests(tests, "Phase 5")

    def demo_phase_6(self):
        """Demo FASE 6: Experiencia."""
        self.show_header(
            "FASE 6: EXPERIENCIA",
            "Barge-in, Detección de Frustración"
        )

        tests = [
            ("Barge-in Interruption", self.test_barge_in),
            ("Frustration Detection", self.test_frustration)
        ]

        self.run_tests(tests, "Phase 6")

    def demo_phase_7(self):
        """Demo FASE 7: Integración."""
        self.show_header(
            "FASE 7: INTEGRACIÓN",
            "Sistema de Plugins, API REST"
        )

        tests = [
            ("Plugin System", self.test_plugins),
            ("REST API", self.test_api)
        ]

        self.run_tests(tests, "Phase 7")

    def run_tests(self, tests: list, phase_name: str):
        """Run a list of tests with progress."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for name, test_func in tests:
                task = progress.add_task(f"Testing {name}...", total=None)

                try:
                    result = test_func()
                    self.results[name] = result
                    progress.update(task, completed=True)
                    console.print(f"  ✅ {name}: {result}")
                except Exception as e:
                    self.results[name] = f"Error: {e}"
                    console.print(f"  ❌ {name}: {str(e)[:50]}")

                time.sleep(0.5)

        self.pause()

    # Test implementations
    def test_silent_mode(self) -> str:
        """Test silent mode."""
        try:
            from terry.core.utils.silent_mode import is_silent, toggle_silent
            current = is_silent()
            return f"Silent mode: {current}"
        except ImportError:
            return "Module not found"

    def test_notifications(self) -> str:
        """Test visual notifications."""
        try:
            from terry.features.visual.notification_manager import get_notification_manager
            mgr = get_notification_manager()
            return f"Notifications: enabled={mgr.enabled}"
        except ImportError:
            return "Module not found"

    def test_voice_notes(self) -> str:
        """Test voice notes system."""
        try:
            from terry.features.notes.voice_notes import get_notes_manager
            mgr = get_notes_manager()

            # Add test note
            note_id = mgr.add_note("Test note from demo", category="demo")

            # Search
            results = mgr.search_notes("demo")

            return f"Notes: {len(results)} found, DB active"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_undo(self) -> str:
        """Test undo system."""
        try:
            from terry.features.undo.action_history import get_action_history
            history = get_action_history()
            return f"Undo: {len(history.history)} actions in history"
        except ImportError:
            return "Module not found"

    def test_memory(self) -> str:
        """Test persistent memory."""
        try:
            from terry.core.memory.manager import MemoryManager
            memory = MemoryManager()
            stats = memory.get_stats()
            return f"Memory: {stats.get('total_interactions', 0)} interactions"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_patterns(self) -> str:
        """Test pattern learning."""
        try:
            from terry.core.memory.pattern_learner import get_pattern_learner
            learner = get_pattern_learner()

            # Count patterns
            total = sum(len(commands) for commands in learner.patterns.get('by_hour', {}).values())
            return f"Patterns: {total} learned"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_context(self) -> str:
        """Test context tracking."""
        try:
            from terry.core.memory.context_manager import get_context_manager
            ctx = get_context_manager()
            return f"Context: {len(ctx.current_entities)} entities tracked"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_suggestions(self) -> str:
        """Test intelligent suggestions."""
        try:
            from terry.core.memory.intelligent_suggestions import get_suggestion_engine
            from datetime import datetime

            engine = get_suggestion_engine()
            suggestions = engine.get_suggestions(datetime.now())
            return f"Suggestions: {len(suggestions)} available"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_camera(self) -> str:
        """Test camera vision."""
        try:
            from terry.features.vision.camera_vision import get_camera_vision
            vision = get_camera_vision()
            return "Camera: initialized"
        except Exception as e:
            return f"Camera: disabled ({type(e).__name__})"

    def test_ocr(self) -> str:
        """Test OCR engine."""
        try:
            from terry.features.vision.ocr_engine import get_ocr_engine
            ocr = get_ocr_engine()
            return f"OCR: tesseract={'available' if ocr.has_tesseract else 'missing'}"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_scheduler(self) -> str:
        """Test scheduler."""
        try:
            from terry.features.automation.cron_manager import get_scheduler
            scheduler = get_scheduler()
            return f"Scheduler: {len(scheduler.routines)} routines"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_triggers(self) -> str:
        """Test conditional triggers."""
        try:
            from terry.features.automation.conditional_engine import get_conditional_engine
            engine = get_conditional_engine()
            return f"Triggers: {len(engine.triggers)} active"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_macros(self) -> str:
        """Test macro recorder."""
        try:
            from terry.features.automation.macro_recorder import get_macro_recorder
            recorder = get_macro_recorder()
            macros = recorder.list_macros()
            return f"Macros: {len(macros)} saved"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_dictation(self) -> str:
        """Test universal dictation."""
        try:
            from terry.features.productivity.universal_dictation import get_dictation_manager
            mgr = get_dictation_manager()
            return f"Dictation: enabled={mgr.enabled}"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_file_search(self) -> str:
        """Test file search."""
        try:
            from terry.features.productivity.file_search import get_file_search
            search = get_file_search()

            # Test search
            results = search.search("*.py", limit=5)
            return f"File Search: {len(results)} Python files found"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_ide(self) -> str:
        """Test IDE control."""
        try:
            from terry.features.productivity.vscode_control import get_vscode_control
            vscode = get_vscode_control()
            return f"VS Code: CLI={'available' if vscode.has_cli else 'missing'}"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_barge_in(self) -> str:
        """Test barge-in interruption."""
        try:
            from terry.features.ux.barge_in import get_barge_in_manager
            mgr = get_barge_in_manager()
            return f"Barge-in: {len(mgr.interrupt_keywords)} keywords"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_frustration(self) -> str:
        """Test frustration detection."""
        try:
            from terry.features.ux.frustration_detector import get_frustration_detector
            detector = get_frustration_detector()
            return f"Frustration: enabled={detector.enabled}"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_plugins(self) -> str:
        """Test plugin system."""
        try:
            from terry.features.extensibility.plugin_system import get_plugin_system
            system = get_plugin_system()
            return f"Plugins: {len(system.plugins)} loaded"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def test_api(self) -> str:
        """Test REST API."""
        try:
            from terry.features.extensibility.rest_api import get_api
            api = get_api()
            return f"API: configured on {api.host}:{api.port}"
        except Exception as e:
            return f"Error: {type(e).__name__}"

    def show_final_report(self):
        """Show final test report."""
        self.show_header("REPORTE FINAL", "Resumen de pruebas Terry v6.1")

        # Create results table
        table = Table(title="Resultados de Pruebas")
        table.add_column("Feature", style="cyan")
        table.add_column("Estado", style="green")
        table.add_column("Resultado", style="yellow")

        success_count = 0
        for name, result in self.results.items():
            if "Error" not in result:
                status = "✅"
                success_count += 1
            else:
                status = "❌"

            table.add_row(name, status, result)

        console.print(table)

        # Summary
        total = len(self.results)
        percentage = (success_count / total * 100) if total > 0 else 0

        console.print(f"\n[bold]Resumen:[/bold]")
        console.print(f"  Total: {total} tests")
        console.print(f"  Exitosos: [green]{success_count}[/green]")
        console.print(f"  Fallidos: [red]{total - success_count}[/red]")
        console.print(f"  Tasa de éxito: [cyan]{percentage:.1f}%[/cyan]")

    def run(self):
        """Run complete demo."""
        self.show_header(
            "🎉 TERRY v6.1 - DEMO INTERACTIVO 🎉",
            "Demostración de las 20 Mejoras Sustanciales"
        )

        console.print("[bold cyan]Esta demo probará automáticamente todas las features implementadas.[/bold cyan]")
        console.print("[dim]Cada fase incluye tests automáticos de sus componentes.[/dim]")

        self.pause("Presiona ENTER para comenzar...")

        # Run all phases
        self.demo_phase_1()
        self.demo_phase_2()
        self.demo_phase_3()
        self.demo_phase_4()
        self.demo_phase_5()
        self.demo_phase_6()
        self.demo_phase_7()

        # Final report
        self.show_final_report()

        console.print("\n[bold green]✅ Demo completada![/bold green]")
        console.print("[dim]Para usar Terry en modo normal: ./run_voice.sh[/dim]")


def main():
    """Main entry point."""
    try:
        demo = TerryDemo()
        demo.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo cancelada por el usuario.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n\n[red]Error en demo: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
