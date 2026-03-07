import time
import logging
import os
from typing import Callable, Any

# Ensure logs directory exists
os.makedirs("backend/logs", exist_ok=True)

logging.basicConfig(
    filename='backend/logs/performance.log',
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
perf_logger = logging.getLogger("MedRAG_Performance")

class PerformanceLogger:
    @staticmethod
    def log_execution_time(stage_name: str, duration: float):
        """ Log raw latency profiling """
        perf_logger.info(f"Stage: [{stage_name}] executed in {duration:.4f} seconds")

    @staticmethod
    async def async_profile(stage_name: str, func: Callable, *args, **kwargs) -> Any:
        """ A wrapper to automatically measure asynchronous function latency execution """
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            PerformanceLogger.log_execution_time(stage_name, duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            perf_logger.error(f"Stage: [{stage_name}] FAILED after {duration:.4f} seconds. Error: {e}")
            raise e

performance_logger = PerformanceLogger()
