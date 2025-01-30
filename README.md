# 🌐 Translation Diff Checker

## Overview

Translation Diff Checker is a powerful, easy-to-use Python tool designed to analyze and compare translation files across multiple languages. It helps developers and translators identify translation gaps, track changes, and maintain high-quality multilingual applications.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Maintenance](https://img.shields.io/badge/Maintained-yes-green.svg)](https://github.com/hasanbeder/translation-diff-checker/graphs/commit-activity)

## 🚀 Features

- 📊 Comprehensive translation file comparison
- 🔍 Detect untranslated, new, and changed keys
- 📈 Generate detailed HTML reports
- 🌈 Support for nested JSON translation files
- 💻 Command-line interface
- 📦 Multi-file and multi-language support

## 📋 Requirements

- Python 3.7+
- JSON translation files
- Supported File Format: `.json`

### 🔍 File Format Limitations
- Currently supports only JSON translation files
- Nested JSON structures are supported
- Future roadmap includes support for YAML, TOML, and other translation formats

### JSON File Structure Example
```json
{
    "welcome_message": "Hello, World!",
    "user_profile": {
        "name": "Name",
        "age": "Age"
    }
}
```

## 📚 Documentation

Detailed documentation is available in the `docs` directory:

- [📖 Index](docs/index.md)
- [🛠 Installation](docs/installation.md)
- [🚀 Usage Guide](docs/usage.md)

For the most up-to-date and comprehensive information, please refer to our documentation.

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/hasanbeder/translation-diff-checker.git

# Change directory
cd translation-diff-checker

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage

### Quick Start with Example Files

```bash
# Try with example files
python3 src/translation_diff_checker.py examples/en.json examples/tr.json
```

### Single File Comparison

```bash
python3 src/translation_diff_checker.py en.json tr.json
```

### Multi-File Comparison

```bash
python3 src/translation_diff_checker.py --source-dir source_translations/ --target-dir target_translations/
```

### Output Formats

```bash
# HTML Report (default)
python3 src/translation_diff_checker.py en.json tr.json

# Text Report
python3 src/translation_diff_checker.py en.json tr.json --format text

# JSON Report
python3 src/translation_diff_checker.py en.json tr.json --format json
```

#### Output Format Options
- **HTML**: Interactive, detailed report with charts and styling
- **Text**: Concise console output with key translation statistics
- **JSON**: Machine-readable format for further processing

#### Text Report Example
```
Multi-File Translation Analysis Report
=====================================

File: en.json
-------------
Total Keys: 150
Translated Keys: 120
Completion Percentage: 80%

Untranslated Keys:
- user.profile.advanced_settings
- notifications.email_preferences
```

#### JSON Report Structure
```json
{
    "total_keys": 150,
    "translated_keys": 120,
    "untranslated_keys": ["key1", "key2"],
    "completion_percentage": 80.0
}
```

## 📊 Report Types

1. **Console Output**: Quick summary of translation differences
2. **HTML Report**: Detailed, interactive report with:
   - Translation coverage percentage
   - Untranslated keys
   - New and removed keys
   - Changed translations

## 🌍 Real-World Use Case: Multilingual Software Localization

### Scenario: E-commerce Platform Internationalization

#### Background
You're developing a global e-commerce platform targeting multiple international markets. Your application needs to support translations for:
- Product descriptions
- User interface elements
- Error messages
- Email templates
- Customer support sections

#### Translation Management Challenges
- 1000+ translation keys across different application domains
- Translations managed by multiple teams
- Need to track translation progress
- Ensure consistency across languages
- Validate translation quality

#### How Translation Diff Checker Helps

1. **Initial Translation Coverage**
```bash
# Compare English base translations with target languages
python3 src/translation_diff_checker.py \
    translations/base/en.json \
    translations/target/es-ES.json \
    --output spanish_translation_report.html
```

2. **Detailed Insights**
The generated report reveals:
- 🔍 Total translation keys: 1000
- ✅ Translated keys: 750
- ❌ Missing keys: 250
- 📊 Completion: 75%

3. **Identifying Translation Gaps**
Report highlights untranslated critical sections:
```
Untranslated Keys:
- checkout.payment_methods
- product.technical_specifications
- user_account.subscription_management
- customer_support.faq_section
```

4. **Continuous Integration**
Integrate into localization workflow:
```yaml
# CI Pipeline Translation Check
localization_check:
  script:
    - python translation-diff-checker.py 
      translations/base/en.json 
      translations/target/fr-FR.json 
      --format text
  only:
    - merge_requests
```

5. **Translator Collaboration**
- Generate comprehensive HTML reports
- Clearly communicate translation requirements
- Track progress across multiple languages
- Prioritize translation efforts

#### Business Impact
- 🌐 Faster global market expansion
- 💡 Systematic translation management
- 📈 Improved user experience
- 💰 Reduced localization costs
- 🚀 Consistent brand messaging

### When to Use
- Before international product launch
- During continuous localization
- After major feature updates
- When adding new language support

### Pro Tips
- Run checks weekly
- Set minimum translation completeness (90%)
- Involve native speakers in review
- Use reports for translator performance tracking

## 🧪 Testing

```bash
# Run tests
python3 -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Issues

Report issues at: https://github.com/hasanbeder/translation-diff-checker/issues

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📧 Contact

Hasan Beder - [@hasanbeder](https://x.com/hasanbeder)

Project Link: [https://github.com/hasanbeder/translation-diff-checker](https://github.com/hasanbeder/translation-diff-checker)

---

**Made with ❤️ for Developers and Translators**
