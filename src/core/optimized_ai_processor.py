"""Оптимизированный AI Processor для Windows:
- ленивость загрузки модели/клиента
- disk-backed cache (SQLite)
- in-memory LRU cache
- история в SQLite и суммаризация старой истории
- интеграция с AIAdapter
"""
import sqlite3
import hashlib
import logging
import threading
import time
import gc
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.core.ai_adapter import AIAdapter

logger = logging.getLogger(__name__)

IN_MEMORY_CACHE_SIZE = 128
CACHE_TTL_SECONDS = 60 * 60

class DiskCache:
    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()
        self.lock = threading.Lock()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                response TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT response, timestamp FROM cache WHERE key=?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            response, ts = row
            if time.time() - ts > CACHE_TTL_SECONDS:
                cur.execute("DELETE FROM cache WHERE key=?", (key,))
                self.conn.commit()
                return None
            return response

    def set(self, key: str, response: str):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("REPLACE INTO cache (key, response, timestamp) VALUES (?, ?, ?)",
                        (key, response, time.time()))
            self.conn.commit()

    def clear_expired(self):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM cache WHERE timestamp < ?", (time.time() - CACHE_TTL_SECONDS,))
            self.conn.commit()

class LRUCache:
    def __init__(self, max_size=IN_MEMORY_CACHE_SIZE):
        self.max_size = max_size
        self.data = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            try:
                value, ts = self.data.pop(key)
                if time.time() - ts > CACHE_TTL_SECONDS:
                    return None
                self.data[key] = (value, time.time())
                return value
            except KeyError:
                return None

    def set(self, key, value):
        with self.lock:
            if key in self.data:
                self.data.pop(key)
            self.data[key] = (value, time.time())
            while len(self.data) > self.max_size:
                self.data.popitem(last=False)

    def clear(self):
        with self.lock:
            self.data.clear()

class OptimizedAI:
    def __init__(self, config=None):
        self.config = config
        self._model = None
        self._model_lock = threading.Lock()
        self.disk_cache = DiskCache()
        self.mem_cache = LRUCache()
        self.chat_history_db = Path("data/chat_history.sqlite")
        self.chat_history_db.parent.mkdir(parents=True, exist_ok=True)
        self._init_history_db()
        self.max_history_items_in_memory = 12
        self.summary_threshold = 300
        self.adapter = AIAdapter(provider='gemini')
        self.system_prompt = (
            "You are Aura, a sophisticated, highly capable, and extremely polite AI assistant, "
            "modeled after JARVIS from Iron Man. You assist the user with their computer tasks, "
            "provide information, and manage system controls. Always address the user as 'Sir' or 'Sirs'. "
            "Your tone should be professional, witty, and helpful. "
            "When asked to open something or perform a system task, confirm it concisely and politely."
        )
        logger.info("OptimizedAI initialized with Jarvis-like personality")

    def _init_history_db(self):
        self.conn_hist = sqlite3.connect(str(self.chat_history_db), check_same_thread=False)
        cur = self.conn_hist.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp REAL
            )
        """)
        self.conn_hist.commit()

    def _lazy_load_model(self):
        # Используем адаптер; реальная загрузка модели не требуется для remote provider
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    logger.info("Lazy load: initializing remote/local model client if needed")
                    # Для remote provider адаптер сам использует ключи по запросу
                    self._model = self.adapter
        return self._model

    def _hash_query(self, prompt: str) -> str:
        import hashlib
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()

    def save_history(self, role: str, content: str):
        cur = self.conn_hist.cursor()
        cur.execute("INSERT INTO history (role, content, timestamp) VALUES (?, ?, ?)",
                    (role, content, time.time()))
        self.conn_hist.commit()
        cur.execute("SELECT COUNT(*) FROM history")
        count = cur.fetchone()[0]
        if count > self.summary_threshold:
            threading.Thread(target=self.summarize_old_history, daemon=True).start()

    def load_recent_history(self, limit: int = 12) -> List[Dict[str, Any]]:
        cur = self.conn_hist.cursor()
        cur.execute("SELECT role, content, timestamp FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        history = []
        for role, content, ts in reversed(rows):
            history.append({'role': role, 'content': content, 'timestamp': ts})
        return history

    def summarize_old_history(self):
        try:
            logger.info("Start summarizing old history...")
            cur = self.conn_hist.cursor()
            cur.execute("SELECT id, role, content FROM history ORDER BY id ASC")
            rows = cur.fetchall()
            if len(rows) <= self.summary_threshold:
                return
            keep = self.max_history_items_in_memory
            to_compress = rows[:-keep]
            if not to_compress:
                return
            combined = "\n".join(f"{r[1]}: {r[2]}" for r in to_compress[-500:])
            summary_text = f"Summary: {combined[:4000]}"
            cur.execute("DELETE FROM history WHERE id IN ({seq})".format(
                seq=",".join(str(r[0]) for r in to_compress)
            ))
            cur.execute("INSERT INTO history (role, content, timestamp) VALUES (?, ?, ?)",
                        ("system_summary", summary_text, time.time()))
            self.conn_hist.commit()
            logger.info("Summarization completed")
        except Exception:
            logger.exception("Error summarizing history")

    def process_command(self, command: str, use_cache: bool = True) -> str:
        recent = self.load_recent_history(limit=self.max_history_items_in_memory)
        context = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
        prompt = f"System: {self.system_prompt}\n{context}\nUser: {command}"
        key = self._hash_query(prompt)

        cached = self.mem_cache.get(key)
        if use_cache and cached:
            logger.debug("Hit in-memory cache")
            return cached

        diskv = self.disk_cache.get(key)
        if use_cache and diskv:
            logger.debug("Hit disk cache")
            self.mem_cache.set(key, diskv)
            return diskv

        model = self._lazy_load_model()
        try:
            # adapter handles remote call
            response = model.chat(prompt, max_tokens=512, temperature=0.2)
        except Exception:
            logger.exception("Adapter chat failed, falling back to simulation")
            response = f"[SIMULATED] Ответ на: {command[:200]}"

        self.disk_cache.set(key, response)
        self.mem_cache.set(key, response)
        self.save_history("user", command)
        self.save_history("assistant", response)
        return response

    def on_memory_pressure(self):
        logger.info("on_memory_pressure: clearing caches and unloading model")
        try:
            self.mem_cache.clear()
            self.disk_cache.clear_expired()
            with self._model_lock:
                if self._model is not None:
                    try:
                        if hasattr(self._model, "unload"):
                            self._model.unload()
                    except Exception:
                        pass
                    self._model = None
            gc.collect()
            logger.info("Resources freed")
        except Exception:
            logger.exception("Error freeing resources")
