# CHANGELOG

## [Unreleased]

### Added
- Windows-optimized AI pipeline (OptimizedAI) — lazy loading, LRU + disk cache
- Gemini AI adapter (configurable via GEMINI_API_KEY / GEMINI_MODEL)
- TTS caching on disk
- Memory monitor to free resources under pressure
- Hotkey listener (Alt+A) using Win32 RegisterHotKey
- Windows-specific command executor
- PyInstaller spec and Inno Setup template
- GitHub Actions workflow for Windows (tests + build + auto-issue on failure)
- Adaptive Learning System (`src/ml/adaptive_learning.py`) to optimize frequent commands
- Custom command mapping (`src/core/custom_commands.py`) to launch local files and directories
- Simplified SVG avatars (`src/ui/avatars.py`) with IDLE, LISTENING, THINKING, SPEAKING states
- Built-in test runner (`src/core/built_in_tester.py`)

### Changed
- Core refactor to reduce memory usage and improve startup performance
- Removed heavy `numpy` dependency to resolve installation and execution issues
