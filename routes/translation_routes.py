from flask import Blueprint, jsonify, request
from utils.translation_checker import TranslationQualityChecker

translation_bp = Blueprint('translation', __name__)
checker = TranslationQualityChecker()

@translation_bp.route('/api/check-translation', methods=['POST'])
def check_translation():
    """
    API endpoint to check translation quality.
    
    Expected JSON payload:
    {
        "source_text": "Original text",
        "translated_text": "Translated text",
        "source_lang": "en/nl/ar",
        "target_lang": "en/nl/ar"
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ['source_text', 'translated_text', 'source_lang', 'target_lang']):
        return jsonify({
            'error': 'Missing required fields',
            'required_fields': ['source_text', 'translated_text', 'source_lang', 'target_lang']
        }), 400

    passed, results = checker.verify_translation(
        data['source_text'],
        data['translated_text'],
        data['source_lang'],
        data['target_lang']
    )
    
    return jsonify({
        'passed': passed,
        'results': results
    })

@translation_bp.route('/api/supported-languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages for translation checking."""
    return jsonify({
        'supported_languages': TranslationQualityChecker.SUPPORTED_LANGUAGES
    })
