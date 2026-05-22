"""
Встроенный тестер для проверки всех компонентов Aura
"""

import unittest
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class TestAdaptiveLearning(unittest.TestCase):
    def test_learning_level_calculation(self):
        from src.ml.adaptive_learning import AdaptiveLearningSystem, LearningLevel
        system = AdaptiveLearningSystem()
        # Test levels based on execution count
        self.assertEqual(system._calculate_learning_level(0), LearningLevel.UNKNOWN)
        self.assertEqual(system._calculate_learning_level(1), LearningLevel.LEARNING)
        self.assertEqual(system._calculate_learning_level(3), LearningLevel.LEARNING)
        self.assertEqual(system._calculate_learning_level(4), LearningLevel.FAMILIAR)
        self.assertEqual(system._calculate_learning_level(7), LearningLevel.FAMILIAR)
        self.assertEqual(system._calculate_learning_level(8), LearningLevel.MASTERED)
        self.assertEqual(system._calculate_learning_level(9), LearningLevel.MASTERED)
        self.assertEqual(system._calculate_learning_level(10), LearningLevel.PERFECTED)
        self.assertEqual(system._calculate_learning_level(15), LearningLevel.PERFECTED)

    def test_train_on_command(self):
        from src.ml.adaptive_learning import AdaptiveLearningSystem, LearningLevel
        system = AdaptiveLearningSystem()
        # Clear database for testing
        system.command_patterns.clear()
        
        level = system.train_on_command("открой хром", "Открываю Chrome", success=True, response_time=0.1)
        self.assertEqual(level, LearningLevel.LEARNING)
        self.assertIn("открой хром", system.command_patterns)
        self.assertEqual(system.command_patterns["открой хром"].execution_count, 1)

class TestCustomCommands(unittest.TestCase):
    def test_add_and_get_command(self):
        from src.core.custom_commands import CustomCommandsManager
        import os
        
        # Use a temporary test json file
        test_file = "data/test_custom_commands.json"
        manager = CustomCommandsManager(filepath=test_file)
        manager.commands.clear()
        
        manager.add_command("открой проект", "D:\\AURA")
        path = manager.get_path_for_command("Aura открой проект")
        self.assertEqual(path, "D:\\AURA")
        
        # Clean up
        if os.path.exists(test_file):
            try:
                os.remove(test_file)
            except Exception:
                pass

class TestAvatars(unittest.TestCase):
    def test_avatar_states(self):
        from src.ui.avatars import AvatarManager, AvatarState
        import shutil
        
        test_dir = "assets/test_avatars"
        manager = AvatarManager(avatar_dir=test_dir)
        
        self.assertEqual(manager.get_current_state(), AvatarState.IDLE)
        manager.set_state(AvatarState.THINKING)
        self.assertEqual(manager.get_current_state(), AvatarState.THINKING)
        
        # Check files exist
        self.assertTrue(Path(manager.get_avatar(AvatarState.IDLE)).exists())
        self.assertTrue(Path(manager.get_avatar(AvatarState.LISTENING)).exists())
        self.assertTrue(Path(manager.get_avatar(AvatarState.THINKING)).exists())
        self.assertTrue(Path(manager.get_avatar(AvatarState.SPEAKING)).exists())
        
        # Clean up
        if Path(test_dir).exists():
            try:
                shutil.rmtree(test_dir)
            except Exception:
                pass

def run_all_tests() -> bool:
    logger.info("========================================")
    logger.info(" Запуск встроенного тестирования Aura... ")
    logger.info("========================================")
    
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAdaptiveLearning))
    suite.addTest(unittest.makeSuite(TestCustomCommands))
    suite.addTest(unittest.makeSuite(TestAvatars))
    
    # Also load external tests from tests/ directory if any
    loader = unittest.TestLoader()
    try:
        external_suite = loader.discover('tests', pattern='test_*.py')
        suite.addTest(external_suite)
    except Exception:
        logger.warning("Не удалось обнаружить тесты в каталоге 'tests'")
        
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    logger.info("========================================")
    logger.info(f"Всего тестов запущено: {result.testsRun}")
    if result.wasSuccessful():
        logger.info("🟢 Тестирование завершено успешно! Ошибок нет.")
        return True
    else:
        logger.error(f"🔴 Тестирование провалено: {len(result.failures)} провалов, {len(result.errors)} ошибок.")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    run_all_tests()
