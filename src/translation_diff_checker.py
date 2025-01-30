#!/usr/bin/env python3
import os
import json
import argparse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

__version__ = "0.2.0"

def count_keys_recursively(source_dict: Dict[str, Any], target_dict: Dict[str, Any], prefix: str = '', top_level: bool = True) -> List[Tuple[str, bool]]:
    """
    Recursively count keys in a nested dictionary and check if they are translated.
    
    Args:
        source_dict (dict): Source language dictionary
        target_dict (dict): Target language dictionary
        prefix (str): Current key path
        top_level (bool): Whether this is the top-level dictionary
    
    Returns:
        list: List of tuples (key_path, is_translated)
    """
    result = []
    
    for key, value in source_dict.items():
        current_key = f"{prefix}{key}" if prefix else key
        
        # If the value is a dictionary, recursively process it
        if isinstance(value, dict):
            # Check if the nested dictionary is fully translated
            if top_level:
                is_nested_translated = (
                    key in target_dict and 
                    isinstance(target_dict.get(key), dict) and
                    all(
                        k in target_dict.get(key, {}) and 
                        target_dict[key][k] is not None and 
                        target_dict[key][k] != ''
                        for k in value.keys()
                    )
                )
                result.append((current_key, is_nested_translated))
            
            # Recursively process nested dictionary
            if key in target_dict and isinstance(target_dict.get(key), dict):
                count_keys_recursively(
                    value, 
                    target_dict[key], 
                    prefix=f"{current_key}.",
                    top_level=False
                )
        else:
            # For non-dictionary values, check if the key is translated
            is_translated = (
                key in target_dict and 
                target_dict[key] is not None and 
                target_dict[key] != ''
            )
            result.append((current_key, is_translated))
    
    return result

def analyze_translation(source_file: str, target_file: str) -> Dict[str, Any]:
    """
    Analyze translation completeness between source and target files.

    Args:
        source_file (str): Path to the source language JSON file
        target_file (str): Path to the target language JSON file

    Returns:
        dict: Translation analysis results
    """
    with open(source_file, 'r', encoding='utf-8') as source_f, \
         open(target_file, 'r', encoding='utf-8') as target_f:
        source_dict = json.load(source_f)
        target_dict = json.load(target_f)

    # Count keys recursively
    key_translations = count_keys_recursively(source_dict, target_dict)

    # Separate translated and untranslated keys
    translated_keys = [key for key, is_translated in key_translations if is_translated]
    untranslated_keys = [key for key, is_translated in key_translations if not is_translated]

    # Calculate statistics
    total_keys = len(key_translations)
    translated_count = len(translated_keys)
    completion_percentage = (translated_count / total_keys) * 100 if total_keys > 0 else 0

    return {
        'total_keys': total_keys,
        'translated_keys': translated_count,
        'missing_keys': [],
        'untranslated_keys': untranslated_keys,
        'completion_percentage': round(completion_percentage, 2)
    }

def find_translation_files(directory: str, pattern: str = '*.json') -> List[str]:
    """
    Find translation files in a directory matching a specific pattern.
    
    Args:
        directory (str): Directory to search for translation files
        pattern (str, optional): File pattern to match. Defaults to '*.json'
    
    Returns:
        list: List of translation file paths
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

def compare_multiple_translations(source_dir: str, target_dir: Optional[str] = None, source_pattern: str = '*.json', target_pattern: str = '*.json') -> Dict[str, Dict[str, Any]]:
    """
    Compare translations across multiple files.
    
    Args:
        source_dir (str): Directory containing source translation files
        target_dir (str, optional): Directory containing target translation files. If None, uses source_dir
        source_pattern (str, optional): Pattern to match source files. Defaults to '*.json'
        target_pattern (str, optional): Pattern to match target files. Defaults to '*.json'
    
    Returns:
        dict: Analysis results for each translation file
    """
    target_dir = target_dir or source_dir
    
    source_files = find_translation_files(source_dir, source_pattern)
    target_files = find_translation_files(target_dir, target_pattern)
    
    results = {}
    
    for source_file in source_files:
        # Find matching target file based on filename
        source_filename = os.path.basename(source_file)
        matching_targets = [tf for tf in target_files if os.path.basename(tf) == source_filename]
        
        if matching_targets:
            target_file = matching_targets[0]
            results[source_filename] = analyze_translation(source_file, target_file)
        else:
            results[source_filename] = {
                'error': f'No matching target file found for {source_filename}'
            }
    
    return results

def detect_translation_directories(repo_path: str) -> List[str]:
    """
    Detect potential translation directories in a Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
    
    Returns:
        list: List of potential translation directory paths
    """
    import os
    
    # Common translation directory names
    translation_dir_patterns = [
        'locales', 
        'translations', 
        'i18n', 
        'lang', 
        'languages', 
        'locale'
    ]
    
    # Potential subdirectories to search
    search_paths = [
        repo_path,
        os.path.join(repo_path, 'src'),
        os.path.join(repo_path, 'public'),
        os.path.join(repo_path, 'assets')
    ]
    
    translation_dirs = []
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        
        for root, dirs, _ in os.walk(search_path):
            for dir_name in dirs:
                # Check if directory name matches translation patterns
                if dir_name in translation_dir_patterns:
                    full_path = os.path.join(root, dir_name)
                    translation_dirs.append(full_path)
    
    return translation_dirs

def find_translation_files_in_repo(repo_path: str, file_pattern: str = '*.json') -> List[str]:
    """
    Find translation files in a Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
        file_pattern (str, optional): File pattern to match. Defaults to '*.json'
    
    Returns:
        list: List of translation file paths
    """
    import glob
    
    translation_dirs = detect_translation_directories(repo_path)
    translation_files = []
    
    for directory in translation_dirs:
        translation_files.extend(
            glob.glob(os.path.join(directory, '**', file_pattern), recursive=True)
        )
    
    return translation_files

def generate_html_report(results: Dict[str, Dict[str, Any]], output_file: Optional[str] = None) -> None:
    """
    Generate an HTML report for multi-file translation analysis.
    
    Args:
        results (dict): Translation analysis results
        output_file (str, optional): Path to save the HTML report
    """
    # Prepare data for the report
    total_files = len(results)
    total_keys = sum(result.get('total_keys', 0) for result in results.values() if not 'error' in result)
    
    # Calculate overall completion percentage
    valid_results = [result for result in results.values() if not 'error' in result]
    completion_percentage = sum(result['completion_percentage'] for result in valid_results) / len(valid_results) if valid_results else 0
    
    # Prepare untranslated keys
    untranslated_keys = {}
    for filename, result in results.items():
        if not 'error' in result and result.get('untranslated_keys'):
            untranslated_keys[filename] = result['untranslated_keys']
    
    # Prepare chart data
    completion_chart_data = [{
        'x': [filename for filename in results.keys() if not 'error' in results[filename]],
        'y': [results[filename]['completion_percentage'] for filename in results.keys() if not 'error' in results[filename]],
        'type': 'bar',
        'marker': {'color': 'green'}
    }]
    completion_chart_json = json.dumps(completion_chart_data)
    
    # Load HTML template
    with open(os.path.join(os.path.dirname(__file__), 'report_template.html'), 'r') as f:
        template_str = f.read()
    
    template = Template(template_str)
    
    # Render HTML report
    html_report = template.render(
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_files=total_files,
        total_keys=total_keys,
        completion_percentage=round(completion_percentage, 2),
        untranslated_keys=untranslated_keys,
        file_details={filename: result for filename, result in results.items() if not 'error' in result},
        completion_chart_data=completion_chart_json
    )
    
    # Save or print the report
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
    else:
        print(html_report)

def generate_multi_file_report(results: Dict[str, Dict[str, Any]], output_file: Optional[str] = None) -> None:
    """
    Generate a report for multi-file translation analysis.
    
    Args:
        results (dict): Translation analysis results
        output_file (str, optional): Path to save the report
    """
    report = "Multi-File Translation Analysis Report\n"
    report += "=====================================\n\n"
    
    for filename, analysis in results.items():
        report += f"File: {filename}\n"
        report += "-" * (len(filename) + 6) + "\n"
        
        if 'error' in analysis:
            report += f"Error: {analysis['error']}\n\n"
        else:
            report += f"Total Keys: {analysis['total_keys']}\n"
            report += f"Translated Keys: {analysis['translated_keys']}\n"
            report += f"Completion Percentage: {analysis['completion_percentage']}%\n"
            
            if analysis['untranslated_keys']:
                report += "\nUntranslated Keys:\n"
                for key in analysis['untranslated_keys']:
                    report += f"- {key}\n"
            
            report += "\n"
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    else:
        print(report)

def find_reference_language_file(translation_files, reference_lang):
    """
    Find the reference language file based on various naming conventions.
    
    Args:
        translation_files (list): List of translation file paths
        reference_lang (str): Reference language identifier
    
    Returns:
        str or None: Path to the reference language file, or None if not found
    """
    # Normalize reference language
    reference_lang = reference_lang.lower()
    
    # Possible naming variations
    lang_variations = [
        reference_lang,                   # 'en'
        f"{reference_lang}.json",         # 'en.json'
        f"translations_{reference_lang}", # 'translations_en'
        f"translations_{reference_lang}.json",  # 'translations_en.json'
        f"messages_{reference_lang}",     # 'messages_en'
        f"messages_{reference_lang}.json" # 'messages_en.json'
    ]
    
    # Normalize file paths and check for variations
    candidates = []
    for file_path in translation_files:
        normalized_path = file_path.lower()
        filename = os.path.basename(normalized_path)
        filename_without_ext = os.path.splitext(filename)[0]
        
        # Check if filename matches any language variations
        for variation in lang_variations:
            variation_without_ext = os.path.splitext(variation)[0]
            if variation == filename or variation_without_ext == filename_without_ext:
                candidates.append(file_path)
                break
    
    # If no candidates found, try more lenient matching
    if not candidates:
        for file_path in translation_files:
            filename = os.path.basename(file_path).lower()
            filename_without_ext = os.path.splitext(filename)[0]
            if reference_lang in filename_without_ext:
                candidates.append(file_path)
    
    # If still no candidates, return None
    if not candidates:
        return None
    
    # If multiple candidates, choose the most comprehensive one
    try:
        # Prioritize files with specific naming conventions
        priority_candidates = []
        for file_path in candidates:
            filename = os.path.basename(file_path).lower()
            filename_without_ext = os.path.splitext(filename)[0]
            if filename_without_ext.startswith('translations_') or filename_without_ext.startswith('messages_'):
                priority_candidates.append(file_path)
        
        # If priority candidates exist, use them
        if priority_candidates:
            candidates = priority_candidates
        
        # Choose the most comprehensive file
        def get_file_length(f):
            try:
                return len(json.load(open(f, 'r', encoding='utf-8')))
            except Exception:
                return 0
        
        reference_file = max(candidates, key=get_file_length)
        return reference_file
    except Exception:
        # If loading fails, return the first candidate
        return candidates[0]

def generate_html_report_for_single_file(analysis_result, source_file, target_file):
    """
    Generate a comprehensive translation gap analysis report
    
    Args:
        analysis_result (dict): Result of translation analysis
        source_file (str): Path to source translation file
        target_file (str): Path to target translation file
    
    Returns:
        str: HTML report content with translation insights
    """
    # Prepare data for visualization
    total_keys = analysis_result['total_keys']
    translated_keys = analysis_result['translated_keys']
    untranslated_keys = analysis_result['untranslated_keys']
    completion_percentage = analysis_result['completion_percentage']
    
    # Categorize completion status
    if completion_percentage > 90:
        status = ("Excellent", "success")
    elif completion_percentage > 75:
        status = ("Good", "primary")
    elif completion_percentage > 50:
        status = ("Needs Work", "warning")
    else:
        status = ("Critical", "danger")
    
    # Load source and target files
    try:
        with open(source_file, 'r', encoding='utf-8') as source_f, \
             open(target_file, 'r', encoding='utf-8') as target_f:
            source_data = json.load(source_f)
            target_data = json.load(target_f)
    except Exception as e:
        source_data = {}
        target_data = {}
    
    # Prepare detailed untranslated keys information
    untranslated_details = []
    for key in untranslated_keys:
        original_text = _find_value_by_key(source_data, key)
        original_text = original_text[0] if isinstance(original_text, tuple) else original_text
        
        untranslated_details.append({
            'key': key,
            'original_text': original_text or 'No original text found',
        })
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Translation Diff Checker: Translation Gap Analysis</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ 
                background-color: #f4f6f9;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }}
            .report-container {{
                max-width: 900px;
                margin: 30px auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .translation-status {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }}
            .progress {{
                height: 30px;
                margin-top: 15px;
            }}
            .translation-gaps {{
                margin-top: 30px;
            }}
            .gap-item {{
                margin-bottom: 15px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 6px;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <h1 class="mb-4">Translation Diff Checker: Translation Gap Analysis</h1>
            
            <div class="translation-status">
                <div>
                    <h3>Translation Status: <span class="text-{status[1]}">{status[0]}</span></h3>
                    <div class="progress">
                        <div class="progress-bar bg-{status[1]}" role="progressbar" 
                             style="width: {completion_percentage}%" 
                             aria-valuenow="{completion_percentage}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                            {completion_percentage:.1f}%
                        </div>
                    </div>
                </div>
                <div>
                    <p><strong>Total Keys:</strong> {total_keys}</p>
                    <p><strong>Translated:</strong> {translated_keys}</p>
                    <p><strong>Untranslated:</strong> {len(untranslated_keys)}</p>
                </div>
            </div>
            
            <div class="translation-gaps">
                <h2>Translation Gaps</h2>
                {"".join(f'''
                <div class="gap-item">
                    <h5 class="text-danger">{detail['key']}</h5>
                    <p class="text-muted">{_truncate_text(detail['original_text'], 200)}</p>
                </div>
                ''' for detail in untranslated_details[:20])}
                
                {"<p class='text-muted'>... and {} more untranslated keys</p>".format(max(0, len(untranslated_details) - 20)) if len(untranslated_details) > 20 else ""}
            </div>
            
            <div class="mt-4 text-center text-muted">
                <small>Generated by Translation Diff Checker</small>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def compare_translation_files(source_file: str, target_file: str) -> Dict[str, Any]:
    """
    Comprehensively compare two translation JSON files and detect differences.
    
    Args:
        source_file (str): Path to the source (original) translation file
        target_file (str): Path to the target (translated) translation file
    
    Returns:
        dict: Detailed comparison of translation files
    """
    def flatten_dict(d, parent_key='', sep='.'):
        """Flatten a nested dictionary for easier comparison."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    try:
        with open(source_file, 'r', encoding='utf-8') as source_f, \
             open(target_file, 'r', encoding='utf-8') as target_f:
            source_dict = json.load(source_f)
            target_dict = json.load(target_f)
    except Exception as e:
        print(f"Error reading files: {e}")
        return {}
    
    # Flatten dictionaries for easier comparison
    source_flat = flatten_dict(source_dict)
    target_flat = flatten_dict(target_dict)
    
    # Detect different types of changes
    untranslated_keys = [
        key for key in source_flat.keys() 
        if key not in target_flat or 
           not target_flat.get(key) or 
           target_flat.get(key) == ''
    ]
    
    removed_keys = [
        key for key in source_flat.keys() 
        if key not in target_flat
    ]
    
    new_keys = [
        key for key in target_flat.keys() 
        if key not in source_flat
    ]
    
    changed_keys = [
        key for key in source_flat.keys() 
        if key in target_flat and 
           source_flat[key] != target_flat[key]
    ]
    
    # Prepare detailed information about changes
    details = {
        'total_source_keys': len(source_flat),
        'total_target_keys': len(target_flat),
        'untranslated_keys': [
            {
                'key': key, 
                'original_text': source_flat.get(key, 'N/A')
            } for key in untranslated_keys
        ],
        'removed_keys': [
            {
                'key': key, 
                'original_text': source_flat.get(key, 'N/A')
            } for key in removed_keys
        ],
        'new_keys': [
            {
                'key': key, 
                'new_text': target_flat.get(key, 'N/A')
            } for key in new_keys
        ],
        'changed_keys': [
            {
                'key': key, 
                'original_text': source_flat.get(key, 'N/A'),
                'new_text': target_flat.get(key, 'N/A')
            } for key in changed_keys
        ]
    }
    
    return details

def generate_translation_comparison_report(source_file: str, target_file: str, output_file: Optional[str] = None) -> str:
    """
    Generate a detailed HTML report comparing two translation files.
    
    Args:
        source_file (str): Path to the source translation file
        target_file (str): Path to the target translation file
        output_file (str, optional): Path to save the HTML report
    
    Returns:
        str: HTML report content or error report
    """
    # Dosya varlığını ve erişilebilirliğini kontrol et
    if not os.path.exists(source_file):
        error_message = f"Source file not found: {source_file}"
        print(error_message)
        error_html = _generate_error_html(error_message, source_file, target_file)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(error_html)
            except IOError as e:
                print(f"Error writing to output file: {e}")
        
        return error_html

    if not os.path.exists(target_file):
        error_message = f"Target file not found: {target_file}"
        print(error_message)
        error_html = _generate_error_html(error_message, source_file, target_file)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(error_html)
            except IOError as e:
                print(f"Error writing to output file: {e}")
        
        return error_html

    # Karşılaştırma sonucunu al
    comparison_result = compare_translation_files(source_file, target_file)
    
    # Karşılaştırma sonucu boşsa hata raporu oluştur
    if not comparison_result:
        error_message = f"Unable to compare files: {source_file} and {target_file}"
        print(error_message)
        error_html = _generate_error_html(error_message, source_file, target_file)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(error_html)
            except IOError as e:
                print(f"Error writing to output file: {e}")
        
        return error_html

    # Extract language names from file paths
    source_lang = os.path.splitext(os.path.basename(source_file))[0]
    target_lang = os.path.splitext(os.path.basename(target_file))[0]
    report_generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate translation coverage and status
    total_source_keys = comparison_result['total_source_keys']
    total_target_keys = comparison_result['total_target_keys']
    untranslated_count = len(comparison_result['untranslated_keys'])
    removed_count = len(comparison_result['removed_keys'])
    new_count = len(comparison_result['new_keys'])
    changed_count = len(comparison_result['changed_keys'])
    
    # Calculate translation coverage percentage
    total_keys = total_source_keys + new_count
    translation_coverage = ((total_target_keys - removed_count) / total_keys * 100) if total_keys > 0 else 0
    
    # Determine translation status
    if translation_coverage == 100 and untranslated_count == 0:
        translation_status = "✅ Complete"
    elif translation_coverage >= 90:
        translation_status = "🟡 Nearly Complete"
    elif translation_coverage >= 50:
        translation_status = "🚧 Partial"
    else:
        translation_status = "❌ Minimal"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Translation Diff Checker: Translation Diff: {source_lang} → {target_lang}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ 
                background-color: #f4f6f9;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }}
            .report-container {{
                max-width: 1200px;
                margin: 30px auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            .header-title {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .header-links a {{
                margin-left: 15px;
                color: #6c757d;
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            .header-links a:hover {{
                color: #007bff;
            }}
            .section-description {{
                margin-bottom: 15px;
                color: #6c757d;
            }}
            .x-icon {{
                color: #000000;
            }}
            .x-icon:hover {{
                color: #1DA1F2;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 15px;
                text-align: center;
                border-radius: 8px;
                margin-top: 30px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
            }}
            .footer-links a {{
                color: #6c757d;
                text-decoration: none;
                transition: color 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .footer-links a:hover {{
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <div class="header">
                <div class="header-title">
                    <div>
                        <h1 class="mb-2">Translation Diff Checker</h1>
                        <h5 class="text-muted">
                            Translation Report: {source_lang}.json ↔ {target_lang}.json
                        </h5>
                        <small class="text-muted">Generated on: {report_generation_time}</small>
                    </div>
                    <div class="header-links">
                        <a href="https://github.com/hasanbeder/translation-diff-checker" target="_blank">
                            <i class="fab fa-github"></i> Project
                        </a>
                        <a href="https://x.com/hasanbeder" target="_blank" class="x-icon">
                            <i class="fab fa-x-twitter"></i> X
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3>Overview</h3>
                <p><strong>Source File:</strong> {source_file}</p>
                <p><strong>Target File:</strong> {target_file}</p>
                <p><strong>Total Source Keys:</strong> {total_source_keys}</p>
                <p><strong>Total Target Keys:</strong> {total_target_keys}</p>
                <p><strong>Translation Coverage:</strong> {translation_coverage:.2f}%</p>
                <p><strong>Translation Status:</strong> {translation_status}</p>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Untranslated Keys ({len(comparison_result['untranslated_keys'])})</h4>
                    <button class="btn btn-outline-danger" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#untranslatedKeysCollapse" 
                            aria-expanded="false" aria-controls="untranslatedKeysCollapse">
                        Toggle Untranslated Keys
                    </button>
                </div>
                <div class="card-body collapse" id="untranslatedKeysCollapse">
                    <p class="section-description">
                        <i class="fas fa-info-circle"></i> 
                        These are keys present in the source language that do not have a corresponding translation in the target language. 
                        They represent missing or incomplete translations that need immediate attention.
                    </p>
                    <div class="accordion" id="untranslatedAccordion">
                        {"".join(f'''
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="untranslated-{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#untranslated-content-{idx}">
                                    {detail['key']}
                                </button>
                            </h2>
                            <div id="untranslated-content-{idx}" class="accordion-collapse collapse" 
                                 aria-labelledby="untranslated-{idx}" data-bs-parent="#untranslatedAccordion">
                                <div class="accordion-body">
                                    <p class="text-muted">{_truncate_text(str(detail['original_text']), 500)}</p>
                                </div>
                            </div>
                        </div>
                        ''' for idx, detail in enumerate(comparison_result['untranslated_keys']))}
                    </div>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Removed Keys ({len(comparison_result['removed_keys'])})</h4>
                    <button class="btn btn-outline-warning" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#removedKeysCollapse" 
                            aria-expanded="false" aria-controls="removedKeysCollapse">
                        Toggle Removed Keys
                    </button>
                </div>
                <div class="card-body collapse" id="removedKeysCollapse">
                    <p class="section-description">
                        <i class="fas fa-info-circle"></i> 
                        These keys were present in the source language but have been completely removed in the target language. 
                        This could indicate deprecated or obsolete translations that are no longer needed.
                    </p>
                    <div class="accordion" id="removedAccordion">
                        {"".join(f'''
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="removed-{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#removed-content-{idx}">
                                    {detail['key']}
                                </button>
                            </h2>
                            <div id="removed-content-{idx}" class="accordion-collapse collapse" 
                                 aria-labelledby="removed-{idx}" data-bs-parent="#removedAccordion">
                                <div class="accordion-body">
                                    <p class="text-muted">{_truncate_text(str(detail['original_text']), 500)}</p>
                                </div>
                            </div>
                        </div>
                        ''' for idx, detail in enumerate(comparison_result['removed_keys']))}
                    </div>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>New Keys ({len(comparison_result['new_keys'])})</h4>
                    <button class="btn btn-outline-success" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#newKeysCollapse" 
                            aria-expanded="false" aria-controls="newKeysCollapse">
                        Toggle New Keys
                    </button>
                </div>
                <div class="card-body collapse" id="newKeysCollapse">
                    <p class="section-description">
                        <i class="fas fa-info-circle"></i> 
                        These are keys that exist in the target language but were not present in the source language. 
                        They might represent additional context, new features, or localization-specific content.
                    </p>
                    <div class="accordion" id="newAccordion">
                        {"".join(f'''
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="new-{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#new-content-{idx}">
                                    {detail['key']}
                                </button>
                            </h2>
                            <div id="new-content-{idx}" class="accordion-collapse collapse" 
                                 aria-labelledby="new-{idx}" data-bs-parent="#newAccordion">
                                <div class="accordion-body">
                                    <p class="text-muted">{_truncate_text(str(detail['new_text']), 500)}</p>
                                </div>
                            </div>
                        </div>
                        ''' for idx, detail in enumerate(comparison_result['new_keys']))}
                    </div>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Changed Keys ({len(comparison_result['changed_keys'])})</h4>
                    <button class="btn btn-outline-primary" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#changedKeysCollapse" 
                            aria-expanded="false" aria-controls="changedKeysCollapse">
                        Toggle Changed Keys
                    </button>
                </div>
                <div class="card-body collapse" id="changedKeysCollapse">
                    <p class="section-description">
                        <i class="fas fa-info-circle"></i> 
                        These keys exist in both source and target languages but have different translations. 
                        This indicates updates or modifications in the translation content.
                    </p>
                    <div class="accordion" id="changedAccordion">
                        {"".join(f'''
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="changed-{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#changed-content-{idx}">
                                    {detail['key']}
                                </button>
                            </h2>
                            <div id="changed-content-{idx}" class="accordion-collapse collapse" 
                                 aria-labelledby="changed-{idx}" data-bs-parent="#changedAccordion">
                                <div class="accordion-body">
                                    <p class="text-muted">Original: {_truncate_text(str(detail['original_text']), 250)}</p>
                                    <p class="text-muted">New: {_truncate_text(str(detail['new_text']), 250)}</p>
                                </div>
                            </div>
                        </div>
                        ''' for idx, detail in enumerate(comparison_result['changed_keys']))}
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-links">
                    <a href="https://github.com/hasanbeder/translation-diff-checker" target="_blank">
                        <i class="fab fa-github"></i> GitHub
                    </a>
                </div>
                <div class="text-muted">
                    Translation Diff Checker
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
        except IOError as e:
            print(f"Error writing to output file: {e}")
    
    return html_template

def _find_value_by_key(data, target_key, current_path='', line_info=None):
    """
    Recursively find the value of a key in a nested dictionary with line information
    
    Args:
        data (dict/list): JSON data to search
        target_key (str): Key to find
        current_path (str): Current path in the nested structure
        line_info (dict): Dictionary to store line information
    
    Returns:
        tuple: (value, line_info_dict)
    """
    if line_info is None:
        line_info = {'line': 0, 'path': ''}
    
    if isinstance(data, dict):
        for key, value in data.items():
            line_info['line'] += 1
            new_path = f"{current_path}.{key}" if current_path else key
            
            if key == target_key:
                line_info['path'] = new_path
                return value, line_info
            
            if isinstance(value, (dict, list)):
                result = _find_value_by_key(value, target_key, new_path, line_info)
                if result is not None:
                    return result
    
    elif isinstance(data, list):
        for index, item in enumerate(data):
            line_info['line'] += 1
            result = _find_value_by_key(item, target_key, f"{current_path}[{index}]", line_info)
            if result is not None:
                return result
    
    return None

def _truncate_text(text, max_length=50):
    """
    Truncate text to a specified max length with ellipsis
    """
    if not isinstance(text, str):
        text = str(text)
    
    return (text[:max_length] + '...') if len(text) > max_length else text

def _generate_error_html(error_message: str, source_file: str, target_file: str) -> str:
    """
    Generate a standardized error HTML report.
    
    Args:
        error_message (str): Specific error description
        source_file (str): Path to source translation file
        target_file (str): Path to target translation file
    
    Returns:
        str: HTML error report
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Translation Diff Checker - Error</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .error-container {{
                background-color: white;
                border: 2px solid #ff6b6b;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #ff6b6b;
                text-align: center;
            }}
            .error-details {{
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 15px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Translation Diff Checker - Error</h1>
            <div class="error-details">
                <p><strong>Error Message:</strong> {error_message}</p>
                <p><strong>Source File:</strong> {source_file}</p>
                <p><strong>Target File:</strong> {target_file}</p>
                <p><em>Possible reasons:
                    <br>- Files not found
                    <br>- Invalid JSON format
                    <br>- Permission issues
                </em></p>
            </div>
        </div>
    </body>
    </html>
    """

def main():
    parser = argparse.ArgumentParser(description='Translation Difference Checker')
    parser.add_argument('--version', action='version', 
                        version=f'%(prog)s {__version__}')
    parser.add_argument('source_file', help='Source translation file')
    parser.add_argument('target_file', help='Target translation file')
    parser.add_argument('--format', choices=['html', 'json', 'text'], default='html', 
                        help='Output format for the report')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    result = None
    
    if args.format == 'html':
        output_file = args.output or 'translation_comparison_report.html'
        generate_translation_comparison_report(
            args.source_file, 
            args.target_file, 
            output_file
        )
        print(f"HTML report saved to {output_file}")
    elif args.format == 'json':
        result = compare_translation_files(args.source_file, args.target_file)
        output_file = args.output or 'translation_comparison.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"JSON report saved to {output_file}")
    elif args.format == 'text':
        result = compare_translation_files(args.source_file, args.target_file)
        output_file = args.output or 'translation_comparison.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Translation Comparison Report\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Total Source Keys: {result['total_source_keys']}\n")
            f.write(f"Total Target Keys: {result['total_target_keys']}\n\n")
            
            f.write(f"Untranslated Keys ({len(result['untranslated_keys'])})\n")
            for detail in result['untranslated_keys'][:20]:
                f.write(f"- {detail['key']}: {_truncate_text(str(detail['original_text']), 100)}\n")
            
            f.write(f"\nRemoved Keys ({len(result['removed_keys'])})\n")
            for detail in result['removed_keys'][:20]:
                f.write(f"- {detail['key']}: {_truncate_text(str(detail['original_text']), 100)}\n")
            
            f.write(f"\nNew Keys ({len(result['new_keys'])})\n")
            for detail in result['new_keys'][:20]:
                f.write(f"- {detail['key']}: {_truncate_text(str(detail['new_text']), 100)}\n")
            
            f.write(f"\nChanged Keys ({len(result['changed_keys'])})\n")
            for detail in result['changed_keys'][:20]:
                f.write(f"- {detail['key']}: {_truncate_text(str(detail['original_text']), 50)} → {_truncate_text(str(detail['new_text']), 50)}\n")
        
        print(f"Text report saved to {output_file}")
    
    return result

if __name__ == '__main__':
    main()
