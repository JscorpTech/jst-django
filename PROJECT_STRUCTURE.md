# JST-Django Project Structure

```
jst-django/
│
├── .github/                          # GitHub configurations
│   └── workflows/
│       ├── ci.yml                   # CI pipeline
│       └── release.yml              # Release automation
│
├── assets/                          # Documentation assets
│   └── docs/                        # Screenshots and images
│
├── src/jst_django/                  # Main source code
│   │
│   ├── cli/                         # CLI application
│   │   ├── app.py                  # Typer app initialization
│   │   └── main.py                 # CLI entry point
│   │
│   ├── commands/                    # CLI commands
│   │   ├── __init__.py
│   │   ├── create.py               # ✅ REFACTORED - Project creation
│   │   ├── generate.py             # Module generation
│   │   ├── install.py              # Module installation
│   │   ├── translate.py            # Translation management
│   │   ├── requirements.py         # Dependencies management
│   │   └── init.py                 # Initialization
│   │
│   ├── utils/                       # Utility modules
│   │   ├── __init__.py             # ✅ UPDATED - Clean exports
│   │   ├── api.py                  # ✅ REFACTORED - GitHub API client
│   │   ├── ast_utils.py            # AST manipulation
│   │   ├── base.py                 # ✅ REFACTORED - Base utilities
│   │   ├── code.py                 # Code formatting
│   │   ├── file.py                 # File operations
│   │   ├── logger.py               # ✅ REFACTORED - Logging system
│   │   ├── progress.py             # Progress bars
│   │   └── tokenize.py             # Tokenization
│   │
│   ├── data/                        # Data files
│   ├── stubs/                       # Code generation templates
│   │
│   ├── __init__.py                  # ✅ NEW - Package initialization
│   ├── config.py                    # ✅ NEW - Configuration management
│   ├── constants.py                 # ✅ NEW - Global constants
│   ├── exceptions.py                # ✅ NEW - Custom exceptions
│   └── validators.py                # ✅ NEW - Input validation
│
├── tests/                           # ✅ NEW - Test suite
│   ├── __init__.py
│   ├── test_validators.py          # Validator tests
│   ├── test_config.py              # Config tests
│   └── test_api.py                 # API tests
│
├── .flake8                          # ✅ UPDATED - Flake8 config
├── .gitignore
├── .pre-commit-config.yaml          # ✅ NEW - Pre-commit hooks
├── ARCHITECTURE.md                  # ✅ NEW - Architecture documentation
├── CONTRIBUTING.md                  # ✅ NEW - Contribution guidelines
├── IMPROVEMENTS.md                  # ✅ NEW - Improvements summary
├── Makefile                         # ✅ NEW - Build automation
├── PROJECT_STRUCTURE.md             # ✅ NEW - This file
├── pyproject.toml                   # Project configuration
├── pytest.ini                       # ✅ NEW - Pytest configuration
├── README.md                        # Main documentation
├── requirements-dev.txt             # ✅ NEW - Dev dependencies
└── test.py                          # Experimental test file

```

## File Status Legend

- ✅ **NEW** - Yangi yaratilgan fayl
- ✅ **REFACTORED** - To'liq qayta ishlangan
- ✅ **UPDATED** - Yangilangan
- ⏳ **TODO** - Keyingi bosqichda qayta ishlanadi
- 📝 **UNCHANGED** - O'zgarishsiz qolgan

## Directory Descriptions

### `/src/jst_django/`
Asosiy kod bazasi. Barcha core functionality shu yerda.

**Core files:**
- `config.py` - ConfigManager sinfi, JSON konfiguratsiyalar
- `constants.py` - Magic numberlar, default qiymatlar, xabarlar
- `exceptions.py` - Custom exception hierarchy
- `validators.py` - Input validation utilities

### `/src/jst_django/cli/`
CLI application entry point va konfiguratsiyasi.

### `/src/jst_django/commands/`
Barcha CLI commandlari. Har bir fayl alohida command.

**Priority for refactoring:**
1. ⏳ `generate.py` - Eng katta va murakkab
2. ⏳ `translate.py` - Translation management
3. ⏳ `install.py` - Module installation
4. ⏳ `init.py` - Initialization

### `/src/jst_django/utils/`
Yordamchi funksiyalar va klasslar.

**Refactored:**
- `api.py` - GitHub API, error handling, logging
- `base.py` - ConfigManager integration, error handling
- `logger.py` - Singleton logger, colored output

**Needs refactoring:**
- ⏳ `ast_utils.py` - AST manipulation
- ⏳ `tokenize.py` - Tokenization

### `/tests/`
Test suite. Pytest bilan ishlaydi.

**Current coverage:**
- Validators - ✅ 100%
- Config - ✅ 90%
- API - ✅ 80%

**Needs tests:**
- ⏳ Commands
- ⏳ AST utils
- ⏳ Tokenizer

### Root Configuration Files

#### Development Tools
- `.flake8` - Linting rules
- `.pre-commit-config.yaml` - Git hooks
- `pytest.ini` - Test configuration
- `Makefile` - Build commands
- `requirements-dev.txt` - Dev dependencies

#### Documentation
- `ARCHITECTURE.md` - Architecture overview
- `CONTRIBUTING.md` - How to contribute
- `IMPROVEMENTS.md` - Changes summary
- `PROJECT_STRUCTURE.md` - This file
- `README.md` - Main docs

#### CI/CD
- `.github/workflows/ci.yml` - Continuous integration
- `.github/workflows/release.yml` - Release automation

## File Count Summary

| Category | Count |
|----------|-------|
| Core Python files (new) | 5 |
| Refactored Python files | 4 |
| Test files | 4 |
| Config files | 6 |
| Documentation files | 5 |
| CI/CD workflows | 2 |
| **Total new/updated** | **26** |

## Lines of Code

| Category | Lines |
|----------|-------|
| Production code (total) | ~2,274 |
| New core modules | ~850 |
| Test code | ~243 |
| Documentation | ~1,200 |
| Configuration | ~200 |
| **Total added** | **~2,493** |

## Next Steps (Priority Order)

### High Priority
1. **generate.py refactoring** - Eng muhim va katta fayl
2. **Add more tests** - Coverage oshirish
3. **translate.py refactoring** - Translation boshqaruvi

### Medium Priority
4. **ast_utils.py refactoring** - AST manipulation
5. **tokenize.py refactoring** - Tokenization logic
6. **install.py refactoring** - Module installation

### Low Priority
7. **User documentation** - End-user guide
8. **API documentation** - Developer reference
9. **Tutorial videos** - Video tutorials

## Migration Path

### Phase 1: Core Infrastructure ✅ COMPLETED
- [x] Constants and configuration
- [x] Exception handling
- [x] Validation
- [x] Logging
- [x] Testing infrastructure
- [x] CI/CD setup

### Phase 2: Command Refactoring (IN PROGRESS)
- [x] create.py
- [ ] generate.py (next)
- [ ] translate.py
- [ ] install.py
- [ ] init.py

### Phase 3: Utilities Refactoring
- [ ] ast_utils.py
- [ ] tokenize.py
- [ ] progress.py

### Phase 4: Testing & Documentation
- [ ] Increase test coverage to >80%
- [ ] Complete API documentation
- [ ] User guide
- [ ] Video tutorials

### Phase 5: Advanced Features
- [ ] Plugin system
- [ ] Rollback mechanism
- [ ] Performance optimization
- [ ] Multi-language support

## Maintenance Guidelines

### Adding New Files
1. Follow naming conventions
2. Add comprehensive docstrings
3. Include type hints
4. Write tests
5. Update this documentation

### Modifying Existing Files
1. Run tests before changes
2. Maintain backward compatibility
3. Update docstrings
4. Add/update tests
5. Run all checks (`make check`)

### Before Committing
```bash
make format      # Format code
make lint        # Check style
make test        # Run tests
make check       # All checks
```

## Support

For questions or issues:
1. Check documentation
2. Search existing issues
3. Create new issue with template
4. Join community discussions

---

**Last Updated:** 2025-10-24
**Version:** v4.4.6
**Status:** Phase 1 Complete, Phase 2 In Progress
