# Usage Guide

## Quick Start

The package comes with example translation files to help you get started:

```bash
# Try with example files
python3 src/translation_diff_checker.py examples/en.json examples/tr.json
```

## Basic Usage

### Single File Comparison
Compare two translation files:

```bash
python3 src/translation_diff_checker.py path/to/source.json path/to/target.json
```

### Check Version
View the current version of the tool:

```bash
python3 src/translation_diff_checker.py --version
```

### Output Formats
The tool supports multiple output formats:

```bash
# HTML Report (default)
python3 src/translation_diff_checker.py en.json tr.json

# Text Report
python3 src/translation_diff_checker.py en.json tr.json --format text

# JSON Report
python3 src/translation_diff_checker.py en.json tr.json --format json
```

## Advanced Usage

### Multi-File Comparison
Compare multiple translation files in directories:

```bash
python3 src/translation_diff_checker.py --source-dir source_translations/ --target-dir target_translations/
```

## Example Files

The `examples` directory contains sample translation files:

### English (en.json)
```json
{
    "welcome": {
        "title": "Welcome to our app!",
        "message": "Start exploring our features"
    },
    "navigation": {
        "home": "Home",
        "profile": "Profile",
        "settings": "Settings"
    }
}
```

### Turkish (tr.json)
```json
{
    "welcome": {
        "title": "Uygulamamıza hoş geldiniz!",
        "message": "Özelliklerimizi keşfetmeye başlayın"
    },
    "navigation": {
        "home": "Ana Sayfa",
        "profile": "Profil",
        "settings": "Ayarlar"
    }
}
```

These example files demonstrate:
- Nested JSON structure
- Multiple translation keys
- Real-world translation examples

## Advanced Options
- `--output`: Specify custom output file path
- `--format`: Choose report format (html/text/json)
- `--source-dir`: Compare multiple files in a directory
- `--target-dir`: Specify target translation directory
