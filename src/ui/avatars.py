"""
Система аватарок для Aura (упрощенная)
Включает SVG аватарки в функциональных состояниях
"""

from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AvatarState(Enum):
    """Состояния аватарки"""
    IDLE = "idle"          # Спокойное состояние
    LISTENING = "listening"  # Слушает команду
    THINKING = "thinking"    # Думает над ответом
    SPEAKING = "speaking"    # Говорит ответ

class AvatarManager:
    """Менеджер аватарок Aura"""
    
    def __init__(self, avatar_dir: str = 'assets/avatars'):
        self.avatar_dir = Path(avatar_dir)
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.current_state = AvatarState.IDLE
        
        # Создаем SVG аватарки
        self._create_avatars()
    
    def _create_avatars(self):
        """Создать SVG аватарки в разных состояниях"""
        
        avatars = {
            'idle': self._create_idle_avatar(),
            'listening': self._create_listening_avatar(),
            'thinking': self._create_thinking_avatar(),
            'speaking': self._create_speaking_avatar(),
        }
        
        for state, svg_content in avatars.items():
            file_path = self.avatar_dir / f"aura_{state}.svg"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                logger.info(f"✅ SVG аватарка создана: {state}")
            except Exception as e:
                logger.error(f"Ошибка создания аватарки {state}: {e}")
    
    def _create_idle_avatar(self) -> str:
        """Создать SVG аватарки в спокойном состоянии"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Фон -->
  <circle cx="100" cy="100" r="95" fill="#1abc9c" opacity="0.2"/>
  
  <!-- Голова -->
  <circle cx="100" cy="80" r="40" fill="#1abc9c" stroke="#0f3d33" stroke-width="2"/>
  
  <!-- Глаза -->
  <circle cx="88" cy="70" r="4" fill="#ffffff"/>
  <circle cx="112" cy="70" r="4" fill="#ffffff"/>
  
  <!-- Зрачки -->
  <circle cx="88" cy="70" r="2.5" fill="#000000"/>
  <circle cx="112" cy="70" r="2.5" fill="#000000"/>
  
  <!-- Улыбка -->
  <path d="M 88 85 Q 100 92 112 85" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  
  <!-- Тело -->
  <rect x="70" y="120" width="60" height="50" rx="10" fill="#16a085" stroke="#0f3d33" stroke-width="2"/>
</svg>'''
    
    def _create_listening_avatar(self) -> str:
        """Создать SVG аватарки в режиме слушания"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Фон -->
  <circle cx="100" cy="100" r="95" fill="#1abc9c" opacity="0.3"/>
  
  <!-- Волны слушания -->
  <circle cx="100" cy="100" r="50" fill="none" stroke="#1abc9c" stroke-width="1" opacity="0.8">
    <animate attributeName="r" values="50;70" dur="1.5s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0" dur="1.5s" repeatCount="indefinite"/>
  </circle>
  
  <!-- Голова -->
  <circle cx="100" cy="80" r="40" fill="#1abc9c" stroke="#0f3d33" stroke-width="2"/>
  
  <!-- Глаза -->
  <circle cx="85" cy="70" r="6" fill="#ffffff"/>
  <circle cx="115" cy="70" r="6" fill="#ffffff"/>
  
  <!-- Зрачки -->
  <circle cx="85" cy="70" r="3" fill="#000000"/>
  <circle cx="115" cy="70" r="3" fill="#000000"/>
  
  <!-- О-образный рот -->
  <circle cx="100" cy="88" r="4" fill="none" stroke="#ffffff" stroke-width="1.5"/>
  
  <!-- Тело -->
  <rect x="70" y="120" width="60" height="50" rx="10" fill="#16a085" stroke="#0f3d33" stroke-width="2"/>
</svg>'''
    
    def _create_thinking_avatar(self) -> str:
        """Создать SVG аватарки в режиме обдумывания"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Фон -->
  <circle cx="100" cy="100" r="95" fill="#f39c12" opacity="0.2"/>
  
  <!-- Голова -->
  <circle cx="100" cy="80" r="40" fill="#f39c12" stroke="#e67e22" stroke-width="2"/>
  
  <!-- Глаза (задумчивые) -->
  <path d="M 82 70 Q 88 75 94 70" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M 106 70 Q 112 75 118 70" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  
  <!-- Рот -->
  <path d="M 88 88 Q 100 95 112 88" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  
  <!-- Лампочка над головой -->
  <circle cx="100" cy="25" r="10" fill="#f39c12" stroke="#e67e22" stroke-width="1.5"/>
  <line x1="100" y1="35" x2="100" y2="40" stroke="#e67e22" stroke-width="2"/>
  
  <!-- Тело -->
  <rect x="70" y="120" width="60" height="50" rx="10" fill="#e67e22" stroke="#c0621e" stroke-width="2"/>
</svg>'''
    
    def _create_speaking_avatar(self) -> str:
        """Создать SVG аватарки в режиме речи"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Фон -->
  <circle cx="100" cy="100" r="95" fill="#1abc9c" opacity="0.3"/>
  
  <!-- Голова -->
  <circle cx="100" cy="80" r="40" fill="#1abc9c" stroke="#0f3d33" stroke-width="2"/>
  
  <!-- Глаза -->
  <path d="M 82 72 Q 88 76 94 72" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M 106 72 Q 112 76 118 72" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>
  
  <!-- Открытый рот -->
  <ellipse cx="100" cy="90" rx="8" ry="10" fill="#0f3d33"/>
  
  <!-- Тело -->
  <rect x="70" y="120" width="60" height="50" rx="10" fill="#16a085" stroke="#0f3d33" stroke-width="2"/>
</svg>'''
    
    def get_avatar(self, state: AvatarState) -> str:
        """
        Получить путь к SVG аватарке
        
        Args:
            state: Состояние аватарки
        
        Returns:
            Путь к файлу SVG
        """
        return str(self.avatar_dir / f"aura_{state.value}.svg")
    
    def set_state(self, state: AvatarState):
        """
        Установить состояние аватарки
        
        Args:
            state: Новое состояние
        """
        self.current_state = state
        logger.info(f"👤 Состояние аватарки: {state.value}")
    
    def get_current_state(self) -> AvatarState:
        """Получить текущее состояние аватарки"""
        return self.current_state
