"""Memory monitor: вызывает aura_core.on_memory_pressure() при превышении лимита
"""
import psutil
import threading
import time
import logging

logger = logging.getLogger(__name__)

class MemoryMonitor(threading.Thread):
    def __init__(self, aura_core, max_rss_mb: int = 1200, check_interval: float = 5.0):
        super().__init__(daemon=True)
        self.aura_core = aura_core
        self.max_rss_mb = max_rss_mb
        self.check_interval = check_interval
        self.running = True

    def run(self):
        logger.info("MemoryMonitor started")
        while self.running:
            try:
                proc = psutil.Process()
                rss_mb = proc.memory_info().rss / (1024 * 1024)
                if rss_mb > self.max_rss_mb:
                    logger.warning(f"Memory usage {rss_mb:.1f}MB > {self.max_rss_mb}MB")
                    try:
                        self.aura_core.on_memory_pressure()
                    except Exception:
                        logger.exception("Error handling memory pressure")
                time.sleep(self.check_interval)
            except Exception:
                logger.exception("MemoryMonitor error")
                time.sleep(self.check_interval)

    def stop(self):
        self.running = False
