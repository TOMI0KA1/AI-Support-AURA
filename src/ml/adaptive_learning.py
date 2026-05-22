"""
Адаптивная система обучения AI модели
Модель обучается при каждом взаимодействии пользователя
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)

class LearningLevel(Enum):
    """Уровни обучения команды"""
    UNKNOWN = 0      # Первый раз встречаем команду
    LEARNING = 1     # Видели 1-3 раза
    FAMILIAR = 2     # Видели 4-7 раз
    MASTERED = 3     # Видели 8+ раз
    PERFECTED = 4    # Видели 10+ раз и система оптимизирована

@dataclass
class CommandPattern:
    """Паттерн команды для обучения"""
    command: str
    variations: List[str] = field(default_factory=list)  # Вариации команды
    execution_count: int = 0  # Количество выполнений
    success_count: int = 0    # Количество успешных выполнений
    average_response_time: float = 0.0
    learning_level: LearningLevel = LearningLevel.UNKNOWN
    confidence: float = 0.0   # Уверенность в распознавании (0-1)
    last_used: Optional[str] = None
    first_used: Optional[str] = None
    user_feedback: List[str] = field(default_factory=list)
    optimized_prompt: Optional[str] = None  # Оптимизированный промпт для этой команды
    learned_features: Dict[str, any] = field(default_factory=dict)

class AdaptiveLearningSystem:
    """Система адаптивного обучения для Aura"""
    
    def __init__(self, config=None, ai_processor=None):
        """
        Инициализировать систему обучения
        
        Args:
            config: Конфигурация приложения
            ai_processor: AI Processor для обработки команд
        """
        self.config = config
        self.ai_processor = ai_processor
        
        self.data_dir = Path('data/learning')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.data_dir / 'command_patterns.json'
        self.learning_file = self.data_dir / 'learning_progress.json'
        
        self.command_patterns: Dict[str, CommandPattern] = {}
        self.learning_stats = {
            'total_commands_learned': 0,
            'total_training_samples': 0,
            'overall_confidence': 0.0,
            'last_training': None
        }
        
        # Статистика по категориям
        self.category_stats = defaultdict(lambda: {
            'count': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0
        })
        
        self._load_patterns()
    
    def train_on_command(self, command: str, response: str, success: bool = True,
                        response_time: float = 0.0, user_feedback: Optional[str] = None) -> LearningLevel:
        """
        Обучить систему на новой команде
        
        Args:
            command: Команда пользователя
            response: Ответ AI
            success: Успешно ли выполнена команда
            response_time: Время ответа в секундах
            user_feedback: Отзыв пользователя (положительный/отрицательный)
        
        Returns:
            Новый уровень обучения
        """
        
        command_lower = command.lower().strip()
        
        # Получаем или создаем паттерн команды
        if command_lower not in self.command_patterns:
            self.command_patterns[command_lower] = CommandPattern(
                command=command_lower,
                first_used=datetime.now().isoformat()
            )
            logger.info(f"📚 Новая команда для обучения: '{command_lower}'")
        
        pattern = self.command_patterns[command_lower]
        
        # Обновляем статистику
        pattern.execution_count += 1
        pattern.last_used = datetime.now().isoformat()
        
        if success:
            pattern.success_count += 1
        
        # Рассчитываем уверенность
        pattern.confidence = pattern.success_count / pattern.execution_count
        
        # Обновляем время ответа (экспоненциальное сглаживание)
        if pattern.execution_count == 1:
            pattern.average_response_time = response_time
        else:
            alpha = 0.3  # Коэффициент сглаживания
            pattern.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * pattern.average_response_time
            )
        
        # Добавляем отзыв
        if user_feedback:
            pattern.user_feedback.append(user_feedback)
        
        # Определяем уровень обучения
        old_level = pattern.learning_level
        pattern.learning_level = self._calculate_learning_level(pattern.execution_count)
        
        # Если достигли нового уровня
        if pattern.learning_level != old_level:
            logger.info(f"🎓 Уровень обучения '{command_lower}': {old_level.name} → {pattern.learning_level.name}")
        
        # Если достаточно примеров - создаем оптимизированный промпт
        if pattern.execution_count == 10:  # После 10 выполнений
            self._create_optimized_prompt(command_lower, pattern)
        
        # Если команда полностью выучена
        if pattern.learning_level == LearningLevel.PERFECTED:
            self._optimize_command_execution(command_lower, pattern)
        
        # Сохраняем обновленные паттерны
        self._save_patterns()
        self._update_learning_stats()
        
        return pattern.learning_level
    
    def get_optimized_prompt(self, command: str) -> Optional[str]:
        """
        Получить оптимизированный промпт для команды
        
        Args:
            command: Команда
        
        Returns:
            Оптимизированный промпт или None
        """
        command_lower = command.lower().strip()
        pattern = self.command_patterns.get(command_lower)
        
        if pattern and pattern.optimized_prompt:
            logger.info(f"🔍 Использую оптимизированный промпт для '{command_lower}'")
            return pattern.optimized_prompt
        
        return None
    
    def predict_command_category(self, command: str) -> str:
        """
        Предсказать категорию команды на основе обучения
        
        Args:
            command: Команда
        
        Returns:
            Категория команды
        """
        command_lower = command.lower().strip()
        
        categories = {
            'system': ['открой', 'запусти', 'app', 'application', 'launch'],
            'information': ['расскажи', 'найди', 'ищи', 'search', 'что', 'какой'],
            'media': ['играй', 'музыка', 'видео', 'play', 'music'],
            'document': ['документ', 'файл', 'файла', 'file', 'document'],
            'settings': ['настройка', 'параметр', 'язык', 'settings', 'configure'],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in command_lower:
                    return category
        
        return 'general'
    
    def get_command_suggestion(self, partial_command: str) -> Optional[str]:
        """
        Получить предложение команды на основе обучения
        
        Args:
            partial_command: Неполная команда
        
        Returns:
            Предложенная команда с высокой уверенностью
        """
        partial_lower = partial_command.lower().strip()
        
        suggestions = []
        for cmd, pattern in self.command_patterns.items():
            if partial_lower in cmd and pattern.learning_level.value >= LearningLevel.FAMILIAR.value:
                suggestions.append((cmd, pattern.confidence))
        
        if suggestions:
            # Сортируем по уверенности
            suggestions.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"💡 Предложение команды: '{suggestions[0][0]}' (уверенность: {suggestions[0][1]:.1%})")
            return suggestions[0][0]
        
        return None
    
    def _calculate_learning_level(self, execution_count: int) -> LearningLevel:
        """
        Рассчитать уровень обучения на основе количества выполнений
        """
        if execution_count >= 10:
            return LearningLevel.PERFECTED
        elif execution_count >= 8:
            return LearningLevel.MASTERED
        elif execution_count >= 4:
            return LearningLevel.FAMILIAR
        elif execution_count >= 1:
            return LearningLevel.LEARNING
        else:
            return LearningLevel.UNKNOWN
    
    def _create_optimized_prompt(self, command: str, pattern: CommandPattern):
        """
        Создать оптимизированный промпт после 10 выполнений
        """
        try:
            category = self.predict_command_category(command)
            success_rate = (pattern.success_count / pattern.execution_count) * 100
            
            optimized = f"""
# Оптимизированный промпт для команды: {command}
# Категория: {category}
# Выполнено: {pattern.execution_count} раз
# Успешность: {success_rate:.1f}%
# Уверенность: {pattern.confidence:.1%}

Для команды '{command}':
- Эта команда выучена и оптимизирована
- Типичный формат: {command}
- Средний ответ: быстро и точно
- Вариации: {', '.join(pattern.variations[:3]) if pattern.variations else 'нет'}

Отвечай кратко и точно без лишних деталей.
            """
            
            pattern.optimized_prompt = optimized
            logger.info(f"🎓 Оптимизированный промпт создан для '{command}'")
        
        except Exception as e:
            logger.error(f"Ошибка создания оптимизированного промпта: {e}")
    
    def _optimize_command_execution(self, command: str, pattern: CommandPattern):
        """
        Оптимизировать выполнение полностью выученной команды
        """
        logger.info(f"🚀 Команда '{command}' полностью выучена и оптимизирована!")
        logger.info(f"   📊 Статистика:")
        logger.info(f"   - Выполнено: {pattern.execution_count} раз")
        logger.info(f"   - Успешность: {(pattern.success_count/pattern.execution_count)*100:.1f}%")
        logger.info(f"   - Среднее время: {pattern.average_response_time:.2f}s")
        logger.info(f"   - Уверенность: {pattern.confidence:.1%}")
        
        # Записываем выученные особенности
        pattern.learned_features = {
            'execution_count': pattern.execution_count,
            'success_rate': pattern.success_count / pattern.execution_count,
            'avg_response_time': pattern.average_response_time,
            'confidence': pattern.confidence,
            'category': self.predict_command_category(command),
            'optimal_prompt': pattern.optimized_prompt
        }
    
    def _update_learning_stats(self):
        """
        Обновить общую статистику обучения
        """
        total_patterns = len(self.command_patterns)
        total_executions = sum(p.execution_count for p in self.command_patterns.values())
        
        confidences = [p.confidence for p in self.command_patterns.values() if p.execution_count > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        self.learning_stats = {
            'total_commands_learned': total_patterns,
            'total_training_samples': total_executions,
            'overall_confidence': avg_confidence,
            'last_training': datetime.now().isoformat(),
            'mastered_commands': sum(1 for p in self.command_patterns.values() 
                                   if p.learning_level == LearningLevel.MASTERED or p.learning_level == LearningLevel.PERFECTED),
            'perfected_commands': sum(1 for p in self.command_patterns.values() 
                                    if p.learning_level == LearningLevel.PERFECTED),
        }
    
    def get_learning_stats(self) -> Dict:
        """
        Получить статистику обучения
        """
        return {
            **self.learning_stats,
            'command_patterns': {
                cmd: {
                    'execution_count': p.execution_count,
                    'success_count': p.success_count,
                    'confidence': p.confidence,
                    'learning_level': p.learning_level.name,
                    'average_response_time': p.average_response_time,
                    'last_used': p.last_used
                }
                for cmd, p in list(self.command_patterns.items())[:20]  # Топ 20
            }
        }
    
    def _save_patterns(self):
        """
        Сохранить паттерны команд
        """
        try:
            data = {
                'patterns': {
                    cmd: {
                        'command': p.command,
                        'variations': p.variations,
                        'execution_count': p.execution_count,
                        'success_count': p.success_count,
                        'average_response_time': p.average_response_time,
                        'learning_level': p.learning_level.name,
                        'confidence': p.confidence,
                        'last_used': p.last_used,
                        'first_used': p.first_used,
                        'user_feedback': p.user_feedback,
                        'optimized_prompt': p.optimized_prompt,
                        'learned_features': p.learned_features
                    }
                    for cmd, p in self.command_patterns.items()
                },
                'stats': self.learning_stats
            }
            
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Ошибка сохранения паттернов: {e}")
    
    def _load_patterns(self):
        """
        Загрузить паттерны команд
        """
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for cmd, p_data in data.get('patterns', {}).items():
                        pattern = CommandPattern(
                            command=p_data['command'],
                            variations=p_data.get('variations', []),
                            execution_count=p_data['execution_count'],
                            success_count=p_data['success_count'],
                            average_response_time=p_data['average_response_time'],
                            learning_level=LearningLevel[p_data['learning_level']],
                            confidence=p_data['confidence'],
                            last_used=p_data.get('last_used'),
                            first_used=p_data.get('first_used'),
                            user_feedback=p_data.get('user_feedback', []),
                            optimized_prompt=p_data.get('optimized_prompt'),
                            learned_features=p_data.get('learned_features', {})
                        )
                        self.command_patterns[cmd] = pattern
                    
                    self.learning_stats = data.get('stats', self.learning_stats)
                    logger.info(f"✅ Загружены паттерны обучения: {len(self.command_patterns)} команд")
        
        except Exception as e:
            logger.warning(f"Ошибка загрузки паттернов: {e}")
