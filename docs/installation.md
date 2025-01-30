# Installation Guide

## Requirements

- Python 3.7+
- pip (Python package installer)

## Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/hasanbeder/translation-diff-checker.git
cd translation-diff-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python3 src/translation_diff_checker.py --version
# Should output: translation-diff-checker 0.2.0
```

## Development Installation

For contributors and developers:

1. Clone the repository:
```bash
git clone https://github.com/hasanbeder/translation-diff-checker.git
cd translation-diff-checker
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest tests/
```

## Troubleshooting

If you encounter any issues during installation:

1. Make sure Python 3.7+ is installed:
```bash
python3 --version
```

2. Verify pip is installed:
```bash
pip --version
```

3. Check if all dependencies are installed:
```bash
pip freeze | grep -E "pytest|coverage"
