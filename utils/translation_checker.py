"""
AI-powered translation quality checker for the mosque management platform.
This module helps ensure high-quality translations between Dutch, Arabic, and English.
"""

from typing import Dict, Tuple
import re
from deep_translator import GoogleTranslator
from langdetect import detect
import nltk
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TranslationQualityChecker:
    """Checks the quality of translations between languages."""
    
    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'nl': 'dutch',
        'ar': 'arabic'
    }

    def __init__(self):
        self.translators = {
            'nl': GoogleTranslator(source='nl', target='en'),
            'ar': GoogleTranslator(source='ar', target='en'),
            'en': GoogleTranslator(source='en', target='en')
        }

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        try:
            return detect(text)
        except:
            return 'en'  # Default to English if detection fails

    def calculate_bleu_score(self, reference: str, candidate: str) -> float:
        """Calculate BLEU score between reference and candidate translations."""
        reference_tokens = word_tokenize(reference.lower())
        candidate_tokens = word_tokenize(candidate.lower())
        return sentence_bleu([reference_tokens], candidate_tokens)

    def check_translation_quality(self, source_text: str, translated_text: str, 
                                source_lang: str, target_lang: str) -> Dict:
        """
        Check the quality of a translation between two languages.
        
        Args:
            source_text: Original text
            translated_text: Translated version
            source_lang: Source language code (en/nl/ar)
            target_lang: Target language code (en/nl/ar)
            
        Returns:
            Dict containing quality metrics and suggestions
        """
        # Validate input languages
        if source_lang not in self.SUPPORTED_LANGUAGES or target_lang not in self.SUPPORTED_LANGUAGES:
            return {
                'error': 'Unsupported language combination',
                'supported_languages': list(self.SUPPORTED_LANGUAGES.keys())
            }

        # Convert both texts to English for comparison if they're not already
        source_in_english = (source_text if source_lang == 'en' 
                           else self.translators[source_lang].translate(source_text))
        
        translated_in_english = (translated_text if target_lang == 'en'
                               else self.translators[target_lang].translate(translated_text))

        # Calculate BLEU score
        bleu_score = self.calculate_bleu_score(source_in_english, translated_in_english)

        # Check for missing variables/placeholders
        source_vars = set(re.findall(r'%\([^)]+\)s|\{\{[^}]+\}\}', source_text))
        translated_vars = set(re.findall(r'%\([^)]+\)s|\{\{[^}]+\}\}', translated_text))
        missing_vars = source_vars - translated_vars

        # Detect potential issues
        issues = []
        if bleu_score < 0.5:
            issues.append("The translation might be inaccurate")
        if len(missing_vars) > 0:
            issues.append(f"Missing variables: {', '.join(missing_vars)}")
        if abs(len(source_text.split()) - len(translated_text.split())) > 5:
            issues.append("Significant length difference between source and translation")

        return {
            'quality_score': bleu_score,
            'issues': issues,
            'missing_variables': list(missing_vars),
            'source_language': source_lang,
            'target_language': target_lang,
            'recommendations': self._generate_recommendations(bleu_score, issues)
        }

    def _generate_recommendations(self, bleu_score: float, issues: list) -> list:
        """Generate recommendations based on quality score and issues."""
        recommendations = []
        
        if bleu_score < 0.3:
            recommendations.append("Consider retranslating the text completely")
        elif bleu_score < 0.5:
            recommendations.append("Review the translation for accuracy")
        
        if "Missing variables" in str(issues):
            recommendations.append("Ensure all placeholders are properly transferred")
            
        if "length difference" in str(issues):
            recommendations.append("Check if any content is missing in the translation")
            
        return recommendations

    def verify_translation(self, source_text: str, translated_text: str, 
                         source_lang: str, target_lang: str) -> Tuple[bool, Dict]:
        """
        Verify if a translation meets quality standards.
        
        Returns:
            Tuple of (passed_verification, details)
        """
        results = self.check_translation_quality(
            source_text, translated_text, source_lang, target_lang
        )
        
        # Consider translation verified if:
        # 1. BLEU score is above 0.5
        # 2. No missing variables
        # 3. No critical issues
        passed = (
            results.get('quality_score', 0) > 0.5 and
            not results.get('missing_variables') and
            len(results.get('issues', [])) <= 1
        )
        
        return passed, results
