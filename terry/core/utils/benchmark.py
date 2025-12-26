"""
Home-Alexa - Benchmark de Velocidad
Mide el rendimiento del sistema
"""

import time
import asyncio
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from terry.core.llm.cache import ResponseCache
from terry.core.utils.persistent_cache import get_persistent_cache
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BenchmarkResult:
    """Resultado de un benchmark."""
    test_name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float


class Benchmark:
    """Herramienta para medir rendimiento."""

    @staticmethod
    def measure_time(func, *args, **kwargs) -> float:
        """
        Mide el tiempo de ejecución de una función.

        Returns:
            Tiempo en segundos
        """
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        return end - start

    @staticmethod
    async def measure_time_async(func, *args, **kwargs) -> float:
        """
        Mide el tiempo de ejecución de una función async.

        Returns:
            Tiempo en segundos
        """
        start = time.perf_counter()
        await func(*args, **kwargs)
        end = time.perf_counter()
        return end - start

    @classmethod
    def run_benchmark(
        cls,
        test_name: str,
        func,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """
        Ejecuta un benchmark de una función.

        Args:
            test_name: Nombre del test
            func: Función a medir
            iterations: Número de iteraciones
            *args, **kwargs: Argumentos para la función

        Returns:
            BenchmarkResult con estadísticas
        """
        times: List[float] = []

        print(f"\n🔬 Benchmark: {test_name}")
        print(f"   Iteraciones: {iterations}")

        for i in range(iterations):
            elapsed = cls.measure_time(func, *args, **kwargs)
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"   Progreso: {i+1}/{iterations}", end='\r')

        print()  # Nueva línea después del progreso

        # Calcular estadísticas
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0

        return BenchmarkResult(
            test_name=test_name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev
        )

    @classmethod
    def print_result(cls, result: BenchmarkResult):
        """Imprime resultado de un benchmark."""
        print(f"\n📊 Resultados: {result.test_name}")
        print("-" * 60)
        print(f"  Iteraciones:     {result.iterations}")
        print(f"  Tiempo total:    {result.total_time*1000:.2f} ms")
        print(f"  Promedio:        {result.avg_time*1000:.2f} ms")
        print(f"  Mediana:         {result.median_time*1000:.2f} ms")
        print(f"  Mínimo:          {result.min_time*1000:.2f} ms")
        print(f"  Máximo:          {result.max_time*1000:.2f} ms")
        print(f"  Desv. estándar:  {result.std_dev*1000:.2f} ms")
        print("-" * 60)


def benchmark_response_cache():
    """Benchmark del caché de respuestas rápidas."""
    test_commands = [
        "para la música",
        "sigue",
        "siguiente",
        "hola",
        "abre safari",
        "sube el volumen"
    ]

    def run_cache_lookup():
        for cmd in test_commands:
            ResponseCache.get_quick_response(cmd)

    result = Benchmark.run_benchmark(
        "Caché de Respuestas (6 comandos)",
        run_cache_lookup,
        iterations=1000
    )

    Benchmark.print_result(result)
    return result


def benchmark_persistent_cache():
    """Benchmark del caché persistente."""
    cache = get_persistent_cache()

    # Preparar datos de prueba
    test_data = {
        "intent": "test",
        "actions": [{"type": "test", "params": {}}],
        "response": "test response"
    }

    test_inputs = [f"comando test {i}" for i in range(10)]

    # Guardar en caché
    for input_text in test_inputs:
        cache.set(input_text, test_data)

    def run_persistent_lookup():
        for input_text in test_inputs:
            cache.get(input_text)

    result = Benchmark.run_benchmark(
        "Caché Persistente (10 lookups)",
        run_persistent_lookup,
        iterations=500
    )

    Benchmark.print_result(result)
    return result


def benchmark_import_speed():
    """Benchmark de velocidad de imports."""
    def import_modules():
        # Forzar reimport
        import importlib
        import sys

        modules = [
            'utils.media_detector',
            'llm.response_cache',
            'actions.action_registry'
        ]

        for module in modules:
            if module in sys.modules:
                del sys.modules[module]
            importlib.import_module(module)

    result = Benchmark.run_benchmark(
        "Import de módulos clave",
        import_modules,
        iterations=50
    )

    Benchmark.print_result(result)
    return result


def run_all_benchmarks():
    """Ejecuta todos los benchmarks."""
    print("=" * 60)
    print("HOME-ALEXA - BENCHMARK DE VELOCIDAD")
    print("=" * 60)

    results = []

    # Benchmark 1: Caché de respuestas
    print("\n🔹 Test 1: Caché de Respuestas Rápidas")
    results.append(benchmark_response_cache())

    # Benchmark 2: Caché persistente
    print("\n🔹 Test 2: Caché Persistente")
    results.append(benchmark_persistent_cache())

    # Benchmark 3: Import speed
    print("\n🔹 Test 3: Velocidad de Imports")
    results.append(benchmark_import_speed())

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE BENCHMARKS")
    print("=" * 60)

    for result in results:
        print(f"\n{result.test_name}:")
        print(f"  ⏱️  {result.avg_time*1000:.2f} ms promedio")
        print(f"  📊 {result.median_time*1000:.2f} ms mediana")
        print(f"  🎯 {result.min_time*1000:.2f} ms mínimo")

    print("\n" + "=" * 60)

    # Evaluación de rendimiento
    cache_avg = results[0].avg_time * 1000  # ms
    persistent_avg = results[1].avg_time * 1000  # ms

    print("\n💡 EVALUACIÓN")
    print("-" * 60)

    if cache_avg < 1.0:
        print("✅ Caché rápido: EXCELENTE (< 1 ms)")
    elif cache_avg < 5.0:
        print("✅ Caché rápido: BUENO (< 5 ms)")
    else:
        print("⚠️  Caché rápido: Podría mejorar")

    if persistent_avg < 5.0:
        print("✅ Caché persistente: EXCELENTE (< 5 ms)")
    elif persistent_avg < 20.0:
        print("✅ Caché persistente: BUENO (< 20 ms)")
    else:
        print("⚠️  Caché persistente: Podría mejorar")

    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
