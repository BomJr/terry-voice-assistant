# Contributing to Terry

Thank you for your interest in contributing to Terry! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/Home-Alexa.git
   cd Home-Alexa
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/Home-Alexa.git
   ```

## Development Environment

### Prerequisites

- macOS 12.0 or later (Terry is macOS-specific)
- Python 3.9 - 3.14
- Homebrew
- Ollama (for LLM functionality)

### Setup

1. **Install system dependencies**:
   ```bash
   ./scripts/install/install.sh
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure settings**:
   ```bash
   cp terry/core/config/settings.yaml.example terry/core/config/settings.yaml
   # Edit settings.yaml with your configuration
   ```

5. **Set up Ollama**:
   ```bash
   brew install ollama
   ollama serve
   ollama pull llama3.1
   ```

6. **Grant macOS permissions**:
   - System Preferences > Security & Privacy > Microphone → Enable Terminal
   - System Preferences > Security & Privacy > Accessibility → Enable Terminal
   - See [PERMISSIONS.md](PERMISSIONS.md) for detailed instructions

### Verify Installation

Run the test suite to ensure everything is working:

```bash
./bin/test_all_features.sh
```

## Making Changes

### Branching Strategy

- Create a new branch for each feature or bugfix:
  ```bash
  git checkout -b feature/my-new-feature
  ```
- Use descriptive branch names:
  - `feature/` - New features
  - `fix/` - Bug fixes
  - `docs/` - Documentation updates
  - `refactor/` - Code refactoring
  - `test/` - Test improvements

### Development Workflow

1. **Keep your fork updated**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Make your changes** in your feature branch

3. **Test your changes** thoroughly:
   ```bash
   # Run unit tests
   python3 -m pytest tests/unit/
   
   # Run integration tests
   python3 -m pytest tests/integration/
   
   # Test specific component
   ./scripts/diagnostics/test_components.sh
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new voice gesture for volume control"
   ```

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add Gemini 2.5 integration as LLM alternative
fix: resolve microphone permission issue on macOS Sequoia
docs: update camera configuration guide
refactor: consolidate STT/TTS into voice module
test: add unit tests for conversation manager
```

## Pull Request Process

1. **Update documentation** if needed:
   - Update `CLAUDE.md` for significant changes
   - Update relevant docs in `docs/` folder
   - Add inline code comments for complex logic

2. **Ensure all tests pass**:
   ```bash
   ./bin/test_all_features.sh
   ```

3. **Update CHANGELOG** (if applicable):
   - Add your changes under "Unreleased" section

4. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

5. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill out the PR template completely
   - Reference any related issues
   - Add screenshots/videos for UI changes
   - Wait for CI/CD checks to pass

6. **Code Review**:
   - Address reviewer feedback
   - Make requested changes in new commits
   - Once approved, maintainers will merge

## Code Style Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **Black** for automatic formatting:
  ```bash
  black terry/ tests/
  ```
- Use **flake8** for linting:
  ```bash
  flake8 terry/ tests/
  ```
- Maximum line length: **100 characters**

### Code Organization

- Keep functions small and focused (< 50 lines ideally)
- Use type hints for function parameters and return values:
  ```python
  def process_command(command: str, language: str = "es") -> ActionResult:
      ...
  ```
- Avoid nested code > 3 levels deep
- Use descriptive variable names (avoid single letters except in loops)

### Documentation

- Add docstrings to all public functions/classes:
  ```python
  def execute_action(self, params: Dict[str, Any]) -> ActionResult:
      """
      Execute the action with given parameters.
      
      Args:
          params: Dictionary containing action parameters
          
      Returns:
          ActionResult object with execution status and message
          
      Raises:
          ValueError: If required parameters are missing
      """
  ```

### Naming Conventions

- **Classes**: PascalCase (`CameraVisionManager`, `ActionBase`)
- **Functions/Methods**: snake_case (`execute_action`, `get_status`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private methods**: prefix with `_` (`_validate_params`)

## Testing Requirements

### Required Tests

All new features and bug fixes **must** include tests:

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution (< 1s per test)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Test with real dependencies when possible
   - Moderate execution time (< 10s per test)

3. **E2E Tests** (`tests/e2e/`)
   - Test complete user workflows
   - Can be slower (< 30s per test)

### Test Structure

```python
import pytest
from terry.core.actions.music.spotify_action import SpotifyAction

class TestSpotifyAction:
    def test_play_song_success(self):
        """Test successful song playback."""
        action = SpotifyAction()
        result = action.execute({"song": "Viva La Vida"})
        assert result.success is True
        assert "Reproduciendo" in result.message
        
    def test_play_song_missing_param(self):
        """Test error handling for missing parameters."""
        action = SpotifyAction()
        with pytest.raises(ValueError):
            action.execute({})
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_spotify_action.py

# Specific test
pytest tests/unit/test_spotify_action.py::TestSpotifyAction::test_play_song_success

# With coverage
pytest --cov=terry tests/
```

### Test Coverage

- Aim for **> 80% code coverage** for new code
- Critical paths (voice pipeline, actions) should have **> 90% coverage**
- Check coverage report:
  ```bash
  pytest --cov=terry --cov-report=html tests/
  open htmlcov/index.html
  ```

## Documentation

### Required Documentation

When adding new features, update:

1. **CLAUDE.md**
   - Add to relevant sections
   - Update version number
   - Add to "Known Issues" if applicable

2. **docs/ folder**
   - Create new doc file for major features
   - Use clear markdown formatting
   - Include examples and screenshots

3. **Inline Comments**
   - Explain "why" not "what"
   - Document complex algorithms
   - Add TODO/FIXME with GitHub issue numbers

4. **README.md**
   - Update features list if applicable
   - Add to Quick Start if it affects setup

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Link to related documentation
- Keep up-to-date with code changes

## Adding New Actions

To add a new voice action:

1. Create action class in `terry/core/actions/{category}/`:
   ```python
   from terry.core.actions.base import ActionBase, ActionResult
   
   class MyNewAction(ActionBase):
       def __init__(self):
           super().__init__(
               name="my_action",
               description="Description in Spanish",
               description_en="Description in English"
           )
       
       async def execute(self, params: Dict[str, Any]) -> ActionResult:
           # Implementation
           return ActionResult(success=True, message="Done!")
   ```

2. Register in `terry/core/actions/registry.py`:
   ```python
   from terry.core.actions.{category}.my_action import MyNewAction
   
   # Add to actions_to_register list
   MyNewAction,
   ```

3. Add patterns to `terry/core/llm/cache.py` for instant matching

4. Add tests in `tests/unit/actions/test_my_action.py`

5. Update documentation

## Adding New LLM Providers

See [docs/LLM_ALTERNATIVES.md](docs/LLM_ALTERNATIVES.md) for guide on integrating new LLM providers.

## Questions?

- Open an issue for questions
- Check existing documentation in `docs/`
- Review `CLAUDE.md` for architecture details
- Ask in pull request comments

## License

By contributing to Terry, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Terry! 🎙️
