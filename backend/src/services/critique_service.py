import re
import logging
from typing import Dict, List

def critique_paper(text: str) -> dict:
    """
    Critique paper using basic NLP and heuristics.
    
    Args:
        text: Full document text
        
    Returns:
        Dictionary with clarity, methodology, bias, and structure assessments
    """
    text_lower = text.lower()
    
    critique_result = {
        "clarity": _assess_clarity(text, text_lower),
        "methodology": _assess_methodology(text_lower),
        "bias": _assess_bias(text_lower),
        "structure": _assess_structure(text, text_lower)
    }
    
    return critique_result

def _assess_clarity(text: str, text_lower: str) -> str:
    """Assess writing clarity and readability."""
    issues = []
    
    # Sentence length analysis
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(sentence.split()) for sentence in sentences if len(sentence.strip()) > 5]
    
    if sentence_lengths:
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        if avg_length > 25:
            issues.append("sentences too long")
        elif avg_length < 8:
            issues.append("sentences too short")
    
    # Check for jargon
    jargon_indicators = [
        'aforementioned', 'heretofore', 'wherein', 'whereby', 'thereof',
        'utilize', 'facilitate', 'implement', 'methodology'
    ]
    
    jargon_count = sum(text_lower.count(word) for word in jargon_indicators)
    if jargon_count > 15:
        issues.append("excessive jargon")
    
    # Check for definitions
    definition_indicators = ['defined as', 'refers to', 'means', 'is the', 'called']
    definition_count = sum(text_lower.count(phrase) for phrase in definition_indicators)
    if definition_count < 3 and len(text.split()) > 1000:
        issues.append("lacks definitions")
    
    if not issues:
        return "Good explanation with clear language"
    else:
        return f"Issues found: {', '.join(issues)}"

def _assess_methodology(text_lower: str) -> str:
    """Assess methodology description."""
    methodology_terms = [
        'method', 'methodology', 'approach', 'procedure', 'technique',
        'experiment', 'survey', 'interview', 'analysis', 'statistical'
    ]
    
    found_terms = [term for term in methodology_terms if term in text_lower]
    
    # Check for statistical methods
    stats_terms = [
        'p-value', 'significant', 'correlation', 'regression',
        'anova', 't-test', 'chi-square', 'confidence interval'
    ]
    
    found_stats = [term for term in stats_terms if term in text_lower]
    
    if len(found_terms) < 3:
        return "Methodology not clearly described"
    elif len(found_stats) == 0 and any(term in text_lower for term in ['quantitative', 'statistical', 'data']):
        return "Statistical methods not clearly described"
    else:
        return "Methodology adequately described"

def _assess_bias(text_lower: str) -> str:
    """Assess potential bias in the paper."""
    bias_indicators = [
        'obviously', 'clearly', 'undoubtedly', 'certainly', 'definitely',
        'always', 'never', 'all', 'none', 'everyone', 'no one'
    ]
    
    strong_claims = sum(text_lower.count(word) for word in bias_indicators)
    
    # Check for hedging language (good for reducing bias)
    hedge_words = [
        'might', 'could', 'may', 'possibly', 'perhaps', 'seems to',
        'appears to', 'suggests that', 'indicates that'
    ]
    
    hedge_count = sum(text_lower.count(word) for word in hedge_words)
    
    if strong_claims > hedge_count * 2:
        return "Potential bias detected - strong claims without hedging"
    elif 'limitation' in text_lower and 'bias' in text_lower:
        return "Bias considerations addressed"
    else:
        return "No apparent bias"

def _assess_structure(text: str, text_lower: str) -> str:
    """Assess document structure and organization."""
    # Check for common academic sections
    sections = {
        'abstract': ['abstract'],
        'introduction': ['introduction'],
        'methodology': ['method', 'methodology'],
        'results': ['result', 'findings'],
        'discussion': ['discussion', 'conclusion'],
        'references': ['references', 'bibliography']
    }
    
    found_sections = []
    for section_name, keywords in sections.items():
        if any(keyword in text_lower for keyword in keywords):
            found_sections.append(section_name)
    
    if len(found_sections) >= 4:
        return "Well organized with clear sections"
    elif len(found_sections) >= 2:
        return "Adequately organized but could improve structure"
    else:
        return "Poor organization - lacks clear sections"

def critique(text: str, summary: str) -> dict:
    """
    Perform heuristic critique of research paper.
    
    Args:
        text: Full document text
        summary: Document summary
    
    Returns:
        Dictionary with methodology, writing_flags, limitations, suggestions
    """
    text_lower = text.lower()
    summary_lower = summary.lower()
    
    critique_result = {
        "methodology": [],
        "writing_flags": [],
        "limitations": [],
        "suggestions": []
    }
    
    # Methodology analysis
    methodology_issues = _analyze_methodology(text_lower)
    critique_result["methodology"].extend(methodology_issues)
    
    # Writing and clarity analysis
    writing_issues = _analyze_writing_quality(text)
    critique_result["writing_flags"].extend(writing_issues)
    
    # Limitations analysis
    limitations = _analyze_limitations(text_lower)
    critique_result["limitations"].extend(limitations)
    
    # Generate suggestions
    suggestions = _generate_suggestions(text_lower, critique_result)
    critique_result["suggestions"].extend(suggestions)
    
    return critique_result

def _analyze_methodology(text: str) -> List[str]:
    """Analyze methodology aspects of the paper."""
    issues = []
    
    # Check for methodology terms
    methodology_terms = {
        'experiment': ['experiment', 'experimental', 'trial'],
        'survey': ['survey', 'questionnaire', 'poll'],
        'interview': ['interview', 'interviews', 'interviewed'],
        'qualitative': ['qualitative', 'thematic analysis', 'grounded theory'],
        'quantitative': ['quantitative', 'statistical', 'numerical'],
        'sample_size': ['sample size', 'n =', 'participants', 'subjects'],
        'randomized': ['randomized', 'random assignment', 'control group'],
        'bias': ['bias', 'confounding', 'threats to validity']
    }
    
    found_terms = {}
    for category, terms in methodology_terms.items():
        found = [term for term in terms if term in text]
        if found:
            found_terms[category] = found
    
    if found_terms:
        issues.append(f"Methodology terms found: {', '.join(found_terms.keys())}")
    else:
        issues.append("Limited methodology terminology detected")
    
    # Check for sample size mentions
    sample_patterns = [
        r'n\s*=\s*(\d+)',
        r'sample size.*?(\d+)',
        r'(\d+)\s+participants',
        r'(\d+)\s+subjects'
    ]
    
    sample_sizes = []
    for pattern in sample_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        sample_sizes.extend(matches)
    
    if sample_sizes:
        sizes = [int(s) for s in sample_sizes if s.isdigit()]
        if sizes:
            max_size = max(sizes)
            if max_size < 30:
                issues.append(f"Small sample size detected (n={max_size})")
            else:
                issues.append(f"Sample size mentioned (n={max_size})")
    else:
        issues.append("No explicit sample size found")
    
    # Check for statistical analysis
    stats_terms = [
        'p-value', 'p <', 'significant', 'correlation', 'regression',
        'anova', 't-test', 'chi-square', 'effect size', 'confidence interval'
    ]
    
    found_stats = [term for term in stats_terms if term in text]
    if found_stats:
        issues.append(f"Statistical analysis: {', '.join(found_stats[:3])}")
    else:
        issues.append("Limited statistical analysis terminology")
    
    return issues

def _analyze_writing_quality(text: str) -> List[str]:
    """Analyze writing quality and clarity."""
    issues = []
    
    # Sentence length analysis
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(sentence.split()) for sentence in sentences if len(sentence.strip()) > 5]
    
    if sentence_lengths:
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        if avg_length > 25:
            issues.append(f"Long average sentence length ({avg_length:.1f} words)")
        elif avg_length < 10:
            issues.append(f"Short average sentence length ({avg_length:.1f} words)")
    
    # Passive voice detection (heuristic)
    passive_indicators = [
        r'\bwas\s+\w+ed\b',
        r'\bwere\s+\w+ed\b',
        r'\bbeen\s+\w+ed\b',
        r'\bis\s+\w+ed\b',
        r'\bare\s+\w+ed\b'
    ]
    
    passive_count = 0
    for pattern in passive_indicators:
        passive_count += len(re.findall(pattern, text, re.IGNORECASE))
    
    total_sentences = len([s for s in sentences if len(s.strip()) > 5])
    if total_sentences > 0:
        passive_ratio = passive_count / total_sentences
        if passive_ratio > 0.3:
            issues.append(f"High passive voice usage ({passive_ratio:.1%})")
    
    # Check for hedging language
    hedge_words = [
        'might', 'could', 'may', 'possibly', 'perhaps', 'seems to',
        'appears to', 'suggests that', 'indicates that'
    ]
    
    hedge_count = sum(text.lower().count(word) for word in hedge_words)
    if hedge_count > len(text.split()) * 0.02:  # More than 2% hedging
        issues.append("Frequent hedging language detected")
    
    # Check for clarity issues
    jargon_indicators = [
        'aforementioned', 'heretofore', 'wherein', 'whereby', 'thereof',
        'utilize', 'facilitate', 'implement', 'methodology'
    ]
    
    jargon_count = sum(text.lower().count(word) for word in jargon_indicators)
    if jargon_count > 10:
        issues.append("Academic jargon may affect readability")
    
    return issues

def _analyze_limitations(text: str) -> List[str]:
    """Analyze research limitations and validity threats."""
    limitations = []
    
    # Check for limitations section
    limitations_keywords = [
        'limitation', 'limitations', 'threats to validity',
        'scope', 'boundary', 'constraint', 'restriction'
    ]
    
    found_limitations = [kw for kw in limitations_keywords if kw in text]
    if found_limitations:
        limitations.append("Limitations section present")
    else:
        limitations.append("No explicit limitations discussion found")
    
    # Check for generalizability discussion
    generalizability_terms = [
        'generaliz', 'external validity', 'broader population',
        'applicability', 'transferability'
    ]
    
    if any(term in text for term in generalizability_terms):
        limitations.append("Generalizability addressed")
    else:
        limitations.append("Limited discussion of generalizability")
    
    # Check for data availability
    data_terms = [
        'data available', 'dataset', 'code available', 'reproducible',
        'replication', 'open data', 'github', 'repository'
    ]
    
    if any(term in text for term in data_terms):
        limitations.append("Data/code availability mentioned")
    else:
        limitations.append("No mention of data or code availability")
    
    # Check for ethical considerations
    ethics_terms = [
        'ethics', 'ethical', 'consent', 'irb', 'institutional review',
        'privacy', 'confidentiality', 'anonymous'
    ]
    
    if any(term in text for term in ethics_terms):
        limitations.append("Ethical considerations addressed")
    else:
        limitations.append("Limited ethical considerations discussion")
    
    return limitations

def _generate_suggestions(text: str, critique_result: dict) -> List[str]:
    """Generate improvement suggestions based on analysis."""
    suggestions = []
    
    # Methodology suggestions
    if "Limited methodology terminology" in critique_result["methodology"]:
        suggestions.append("Add detailed methodology section with research design")
    
    if "No explicit sample size found" in critique_result["methodology"]:
        suggestions.append("Include sample size and participant demographics")
    
    if "Limited statistical analysis terminology" in critique_result["methodology"]:
        suggestions.append("Report statistical tests and effect sizes")
    
    # Writing suggestions
    writing_flags = critique_result["writing_flags"]
    if any("Long average sentence length" in flag for flag in writing_flags):
        suggestions.append("Consider shorter, clearer sentences for better readability")
    
    if any("High passive voice" in flag for flag in writing_flags):
        suggestions.append("Reduce passive voice for more direct writing")
    
    if any("Academic jargon" in flag for flag in writing_flags):
        suggestions.append("Simplify technical language where possible")
    
    # Limitations suggestions
    limitations = critique_result["limitations"]
    if "No explicit limitations discussion found" in limitations:
        suggestions.append("Add dedicated limitations section")
    
    if "Limited discussion of generalizability" in limitations:
        suggestions.append("Discuss generalizability and external validity")
    
    if "No mention of data or code availability" in limitations:
        suggestions.append("Consider making data and analysis code available")
    
    # General suggestions
    novelty_terms = ['novel', 'new', 'innovative', 'first', 'original']
    novelty_count = sum(text.count(term) for term in novelty_terms)
    
    if novelty_count < 3:
        suggestions.append("Clarify the novel contributions of this work")
    
    # Check for future work
    if 'future work' not in text and 'future research' not in text:
        suggestions.append("Include discussion of future research directions")
    
    return suggestions[:8]  # Limit to 8 suggestions