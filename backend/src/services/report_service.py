import os
import uuid
from datetime import datetime
import textwrap
import logging
from flask import current_app
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_analysis_report(analysis_results: dict, output_path: str) -> str:
    """
    Generate analysis report PDF using ReportLab.
    
    Args:
        analysis_results: Dictionary containing all analysis results
        output_path: Path where to save the PDF report
        
    Returns:
        Path to the generated PDF report
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2563eb')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#1e40af')
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Title
        story.append(Paragraph("Research Paper Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Document Information
        story.append(Paragraph("Analysis Summary", header_style))
        if 'summary' in analysis_results:
            summary_text = _wrap_text(analysis_results['summary'], 80)
            story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 15))
        
        # Plagiarism Results
        if 'plagiarism' in analysis_results:
            story.append(Paragraph("Plagiarism Analysis", header_style))
            plagiarism = analysis_results['plagiarism']
            
            score = plagiarism.get('plagiarism_score', 0.0)
            score_text = f"Overall Similarity Score: {score:.1%}"
            story.append(Paragraph(score_text, body_style))
            
            if 'matching_sources' in plagiarism and plagiarism['matching_sources']:
                story.append(Paragraph("Top Matching Sources:", body_style))
                for source in plagiarism['matching_sources'][:5]:
                    source_text = f"• {source['file']}: {source['score']:.1%} similarity"
                    story.append(Paragraph(source_text, body_style))
            
            story.append(Spacer(1, 15))
        
        # Citation Validation Results
        if 'citations' in analysis_results:
            story.append(Paragraph("Citation Validation", header_style))
            citations = analysis_results['citations']
            
            valid_count = len([c for c in citations if c.get('valid', False)])
            total_count = len(citations)
            
            validation_text = f"Citations Validated: {valid_count}/{total_count}"
            story.append(Paragraph(validation_text, body_style))
            
            # Show first few citations
            for i, citation in enumerate(citations[:5]):
                status = "✓ Valid" if citation.get('valid', False) else "✗ Invalid"
                doi = f" (DOI: {citation['doi']})" if citation.get('doi') else ""
                citation_text = f"{i+1}. {status}{doi}"
                story.append(Paragraph(citation_text, body_style))
            
            if len(citations) > 5:
                story.append(Paragraph(f"... and {len(citations) - 5} more citations", body_style))
            
            story.append(Spacer(1, 15))
        
        # Critique Feedback
        if 'critique' in analysis_results:
            story.append(Paragraph("Paper Critique", header_style))
            critique = analysis_results['critique']
            
            for aspect, assessment in critique.items():
                aspect_title = aspect.replace('_', ' ').title()
                story.append(Paragraph(f"{aspect_title}: {assessment}", body_style))
            
            story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error generating analysis report: {e}")
        raise Exception(f"Failed to generate report: {str(e)}")

def generate_report(user, document, analysis, citations: list[dict]) -> tuple[str, str]:
    """
    Generate PDF report for analysis results.
    
    Args:
        user: User object
        document: Document object  
        analysis: Analysis object
        citations: List of citation dictionaries
    
    Returns:
        Tuple of (report_id, filepath)
    """
    # Generate unique report ID
    report_id = str(uuid.uuid4())
    
    # Create report filename
    report_dir = current_app.config.get('REPORT_DIR', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    filename = f"analysis_report_{report_id}.pdf"
    filepath = os.path.join(report_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2563eb')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=HexColor('#1e40af'),
        borderWidth=1,
        borderColor=HexColor('#e5e7eb'),
        borderPadding=8,
        backColor=HexColor('#f8fafc')
    )
    
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor=HexColor('#374151')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leftIndent=0,
        rightIndent=0
    )
    
    # Title
    story.append(Paragraph("AI Research Critic - Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Document Information
    story.append(Paragraph("Document Information", header_style))
    doc_info = [
        ['Title:', document.title or 'Untitled'],
        ['Filename:', document.filename],
        ['Word Count:', str(document.word_count)],
        ['Analyzed by:', user.name],
        ['Analysis Date:', analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else 'N/A'],
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    doc_table = Table(doc_info, colWidths=[2*inch, 4*inch])
    doc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f9fafb'), white]),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 20))
    
    # Plagiarism Score
    story.append(Paragraph("Plagiarism Analysis", header_style))
    
    score = analysis.plagiarism_score or 0.0
    score_color = _get_score_color(score)
    
    score_text = f"<font color='{score_color}'><b>{score}%</b></font>"
    story.append(Paragraph(f"Similarity Score: {score_text}", body_style))
    
    score_interpretation = _interpret_plagiarism_score(score)
    story.append(Paragraph(f"Interpretation: {score_interpretation}", body_style))
    story.append(Spacer(1, 15))
    
    # Summary
    if analysis.summary:
        story.append(Paragraph("Document Summary", header_style))
        
        # Wrap long summary text
        wrapped_summary = _wrap_text(analysis.summary, 80)
        story.append(Paragraph(wrapped_summary, body_style))
        story.append(Spacer(1, 15))
    
    # Citations Analysis
    if citations:
        story.append(Paragraph("Citations Analysis", header_style))
        
        # Citation statistics
        total_citations = len(citations)
        valid_citations = len([c for c in citations if c['status'] == 'Valid'])
        not_found = len([c for c in citations if c['status'] == 'Not Found'])
        timeouts = len([c for c in citations if c['status'] == 'API Timeout'])
        errors = len([c for c in citations if c['status'] == 'Error'])
        
        stats_text = f"""
        Total Citations: {total_citations}<br/>
        Valid Citations: {valid_citations}<br/>
        Not Found: {not_found}<br/>
        API Timeouts: {timeouts}<br/>
        Errors: {errors}
        """
        story.append(Paragraph(stats_text, body_style))
        story.append(Spacer(1, 10))
        
        # Citations table (show top 30)
        story.append(Paragraph("Citation Details (Top 30)", subheader_style))
        
        citation_data = [['#', 'Status', 'Title']]
        for i, citation in enumerate(citations[:30], 1):
            status_color = _get_citation_status_color(citation['status'])
            status_text = f"<font color='{status_color}'>{citation['status']}</font>"
            
            # Truncate long titles
            title = citation.get('cleaned_title', citation.get('raw', ''))[:80]
            if len(title) == 80:
                title += "..."
            
            citation_data.append([str(i), Paragraph(status_text, body_style), title])
        
        citation_table = Table(citation_data, colWidths=[0.5*inch, 1*inch, 4.5*inch])
        citation_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f9fafb'), white]),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e5e7eb'))
        ]))
        story.append(citation_table)
        story.append(Spacer(1, 15))
    
    # Critique Analysis
    if analysis.critique:
        story.append(Paragraph("Research Critique", header_style))
        
        critique = analysis.critique
        
        # Methodology
        if critique.get('methodology'):
            story.append(Paragraph("Methodology Analysis", subheader_style))
            for item in critique['methodology']:
                story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 10))
        
        # Writing Quality
        if critique.get('writing_flags'):
            story.append(Paragraph("Writing Quality", subheader_style))
            for item in critique['writing_flags']:
                story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 10))
        
        # Limitations
        if critique.get('limitations'):
            story.append(Paragraph("Research Limitations", subheader_style))
            for item in critique['limitations']:
                story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 10))
        
        # Suggestions
        if critique.get('suggestions'):
            story.append(Paragraph("Improvement Suggestions", subheader_style))
            for item in critique['suggestions']:
                story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 10))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = """
    <i>This report was generated by AI Research Critic, an automated analysis tool. 
    The analysis is based on heuristic methods and should be used as a starting point 
    for manual review rather than a definitive assessment.</i>
    """
    story.append(Paragraph(footer_text, body_style))
    
    # Build PDF
    doc.build(story)
    
    return report_id, filepath

def _wrap_text(text: str, width: int) -> str:
    """Wrap text to specified width."""
    if not text:
        return ""
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []
    
    for paragraph in paragraphs:
        if paragraph.strip():
            wrapped = textwrap.fill(paragraph.strip(), width=width)
            wrapped_paragraphs.append(wrapped)
    
    return '<br/><br/>'.join(wrapped_paragraphs)

def _get_score_color(score: float) -> str:
    """Get color for plagiarism score."""
    if score >= 70:
        return '#dc2626'  # Red
    elif score >= 40:
        return '#ea580c'  # Orange  
    elif score >= 20:
        return '#ca8a04'  # Yellow
    else:
        return '#16a34a'  # Green

def _interpret_plagiarism_score(score: float) -> str:
    """Interpret plagiarism score."""
    if score >= 70:
        return "High similarity detected - manual review strongly recommended"
    elif score >= 40:
        return "Moderate similarity detected - manual review recommended"
    elif score >= 20:
        return "Low similarity detected - acceptable with minor review"
    else:
        return "Minimal similarity detected - acceptable"

def _get_citation_status_color(status: str) -> str:
    """Get color for citation status."""
    colors = {
        'Valid': '#16a34a',      # Green
        'Not Found': '#dc2626',   # Red
        'API Timeout': '#ea580c', # Orange
        'Error': '#7c2d12'        # Dark red
    }
    return colors.get(status, '#374151')  # Default gray