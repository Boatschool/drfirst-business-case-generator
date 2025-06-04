"""
PDF generation utilities for the DrFirst Business Case Generator.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import io

import markdown
from weasyprint import HTML

# Set up logging
logger = logging.getLogger(__name__)

# HTML template for the business case PDF
PDF_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Business Case</title>
    <style>
        {css_styles}
    </style>
</head>
<body>
    <div class="document">
        <!-- Header -->
        <header>
            <div class="header-content">
                <h1 class="doc-title">{title}</h1>
                <div class="doc-metadata">
                    <p><strong>Case ID:</strong> {case_id}</p>
                    <p><strong>Status:</strong> <span class="status-{status_class}">{status}</span></p>
                    <p><strong>Created:</strong> {created_at}</p>
                    <p><strong>Last Updated:</strong> {updated_at}</p>
                </div>
            </div>
        </header>

        <!-- Problem Statement -->
        <section class="section">
            <h2 class="section-title">Problem Statement</h2>
            <div class="content">
                {problem_statement}
            </div>
        </section>

        <!-- Relevant Links -->
        {relevant_links_section}

        <!-- PRD Section -->
        {prd_section}

        <!-- System Design Section -->
        {system_design_section}

        <!-- Financial Analysis -->
        <section class="section financial-analysis">
            <h2 class="section-title">📊 Financial Analysis</h2>
            
            <!-- Effort Estimate -->
            {effort_estimate_section}
            
            <!-- Cost Estimate -->
            {cost_estimate_section}
            
            <!-- Value Projection -->
            {value_projection_section}
            
            <!-- Financial Summary -->
            {financial_summary_section}
        </section>

        <!-- Approval History -->
        {approval_history_section}

        <!-- Footer -->
        <footer>
            <p>Generated on {generation_date} by DrFirst Business Case Generator</p>
        </footer>
    </div>
</body>
</html>
"""

# CSS styles for professional PDF formatting
PDF_CSS_STYLES = """
@page {
    size: A4;
    margin: 2cm 1.5cm;
    @top-center {
        content: "DrFirst Business Case";
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
    margin: 0;
    padding: 0;
}

.document {
    max-width: 100%;
    margin: 0 auto;
}

/* Header Styles */
header {
    border-bottom: 3px solid #1976d2;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.doc-title {
    font-size: 24pt;
    font-weight: bold;
    color: #1976d2;
    margin: 0 0 15px 0;
}

.doc-metadata {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
}

.doc-metadata p {
    margin: 5px 0;
    font-size: 10pt;
}

.status-approved { color: #2e7d32; font-weight: bold; }
.status-pending { color: #f57f17; font-weight: bold; }
.status-rejected { color: #d32f2f; font-weight: bold; }
.status-draft { color: #666; }

/* Section Styles */
.section {
    margin-bottom: 30px;
    page-break-inside: avoid;
}

.section-title {
    font-size: 16pt;
    font-weight: bold;
    color: #1976d2;
    margin: 0 0 15px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e3f2fd;
}

.content {
    line-height: 1.6;
}

/* Markdown Content Styles */
.markdown-content h1 {
    font-size: 14pt;
    font-weight: bold;
    color: #1976d2;
    margin: 20px 0 10px 0;
}

.markdown-content h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #333;
    margin: 18px 0 8px 0;
}

.markdown-content h3 {
    font-size: 12pt;
    font-weight: bold;
    color: #444;
    margin: 15px 0 6px 0;
}

.markdown-content p {
    margin: 8px 0;
}

.markdown-content ul, .markdown-content ol {
    margin: 10px 0;
    padding-left: 20px;
}

.markdown-content li {
    margin: 4px 0;
}

.markdown-content strong {
    font-weight: bold;
    color: #1976d2;
}

.markdown-content em {
    font-style: italic;
}

.markdown-content blockquote {
    border-left: 4px solid #1976d2;
    padding-left: 15px;
    margin: 15px 0;
    font-style: italic;
    background-color: #f8f9fa;
    padding: 10px 15px;
}

.markdown-content code {
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

.markdown-content pre {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

/* Table Styles */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
}

.data-table th {
    background-color: #1976d2;
    color: white;
    padding: 8px;
    text-align: left;
    font-weight: bold;
}

.data-table td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
}

.data-table tr:nth-child(even) {
    background-color: #f8f9fa;
}

/* Financial Styles */
.financial-analysis {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border-left: 5px solid #1976d2;
}

.financial-subsection {
    margin: 20px 0;
    padding: 15px;
    background-color: white;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
}

.financial-subsection h3 {
    color: #1976d2;
    margin-top: 0;
    font-size: 13pt;
}

.currency-amount {
    font-weight: bold;
    color: #2e7d32;
}

.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin: 15px 0;
}

.metric-item {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    border-left: 3px solid #1976d2;
}

.metric-label {
    font-size: 9pt;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 12pt;
    font-weight: bold;
    color: #333;
}

/* Links Styles */
.links-list {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
}

.links-list a {
    color: #1976d2;
    text-decoration: none;
}

/* Footer */
footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    text-align: center;
    color: #666;
    font-size: 9pt;
}

/* Page Break Controls */
.page-break-before {
    page-break-before: always;
}

.page-break-avoid {
    page-break-inside: avoid;
}
"""


async def generate_business_case_pdf(case_data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF document for a business case.
    
    Args:
        case_data (Dict[str, Any]): Business case data from Firestore
        
    Returns:
        bytes: PDF document as bytes
        
    Raises:
        Exception: If PDF generation fails
    """
    try:
        logger.info(f"Starting PDF generation for case {case_data.get('case_id')}")
        
        # Use asyncio.to_thread for the blocking PDF generation
        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, case_data)
        
        logger.info(f"PDF generation completed for case {case_data.get('case_id')}")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"PDF generation failed for case {case_data.get('case_id')}: {str(e)}")
        raise Exception(f"PDF generation failed: {str(e)}")


def _generate_pdf_sync(case_data: Dict[str, Any]) -> bytes:
    """
    Synchronous PDF generation function.
    Called via asyncio.to_thread for async compatibility.
    """
    # Prepare template data
    template_data = _prepare_template_data(case_data)
    
    # Generate HTML content
    html_content = PDF_HTML_TEMPLATE.format(**template_data)
    
    # Create WeasyPrint HTML object
    html_doc = HTML(string=html_content)
    
    # Generate PDF
    pdf_buffer = io.BytesIO()
    html_doc.write_pdf(pdf_buffer)
    
    return pdf_buffer.getvalue()


def _prepare_template_data(case_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepare data for the HTML template.
    """
    # Basic case information
    case_id = case_data.get('case_id', 'N/A')
    title = case_data.get('title', 'Business Case')
    status = case_data.get('status', 'UNKNOWN')
    
    # Format dates
    created_at = _format_datetime(case_data.get('created_at'))
    updated_at = _format_datetime(case_data.get('updated_at'))
    generation_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    
    # Status class for styling
    status_class = status.lower().replace('_', '-')
    
    # Problem statement
    problem_statement = case_data.get('problem_statement', 'No problem statement provided.')
    
    # Relevant links section
    relevant_links_section = _generate_relevant_links_section(case_data.get('relevant_links', []))
    
    # PRD section
    prd_section = _generate_prd_section(case_data.get('prd_draft'))
    
    # System design section
    system_design_section = _generate_system_design_section(case_data.get('system_design_v1_draft'))
    
    # Financial sections
    effort_estimate_section = _generate_effort_estimate_section(case_data.get('effort_estimate_v1'))
    cost_estimate_section = _generate_cost_estimate_section(case_data.get('cost_estimate_v1'))
    value_projection_section = _generate_value_projection_section(case_data.get('value_projection_v1'))
    financial_summary_section = _generate_financial_summary_section(case_data.get('financial_summary_v1'))
    
    # Approval history
    approval_history_section = _generate_approval_history_section(case_data.get('history', []))
    
    return {
        'css_styles': PDF_CSS_STYLES,
        'title': title,
        'case_id': case_id,
        'status': status,
        'status_class': status_class,
        'created_at': created_at,
        'updated_at': updated_at,
        'generation_date': generation_date,
        'problem_statement': problem_statement,
        'relevant_links_section': relevant_links_section,
        'prd_section': prd_section,
        'system_design_section': system_design_section,
        'effort_estimate_section': effort_estimate_section,
        'cost_estimate_section': cost_estimate_section,
        'value_projection_section': value_projection_section,
        'financial_summary_section': financial_summary_section,
        'approval_history_section': approval_history_section,
    }


def _format_datetime(dt) -> str:
    """Format datetime for display."""
    if not dt:
        return 'N/A'
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    try:
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return str(dt)


def _markdown_to_html(markdown_text: str) -> str:
    """Convert markdown text to HTML."""
    if not markdown_text:
        return '<p>No content available.</p>'
    
    try:
        html = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'toc']
        )
        return f'<div class="markdown-content">{html}</div>'
    except Exception as e:
        logger.warning(f"Markdown conversion failed: {e}")
        return f'<div class="content"><pre>{markdown_text}</pre></div>'


def _generate_relevant_links_section(links: list) -> str:
    """Generate HTML for relevant links section."""
    if not links:
        return ''
    
    links_html = '<div class="links-list"><ul>'
    for link in links:
        name = link.get('name', 'Link')
        url = link.get('url', '#')
        links_html += f'<li><a href="{url}">{name}</a></li>'
    links_html += '</ul></div>'
    
    return f'''
    <section class="section">
        <h2 class="section-title">🔗 Relevant Links</h2>
        {links_html}
    </section>
    '''


def _generate_prd_section(prd_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for PRD section."""
    if not prd_data:
        return '''
        <section class="section">
            <h2 class="section-title">📋 Product Requirements Document</h2>
            <div class="content">
                <p><em>PRD not yet generated.</em></p>
            </div>
        </section>
        '''
    
    prd_content = prd_data.get('content_markdown', '')
    prd_html = _markdown_to_html(prd_content)
    version = prd_data.get('version', 'N/A')
    
    return f'''
    <section class="section page-break-before">
        <h2 class="section-title">📋 Product Requirements Document (v{version})</h2>
        {prd_html}
    </section>
    '''


def _generate_system_design_section(system_design_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for system design section."""
    if not system_design_data:
        return '''
        <section class="section">
            <h2 class="section-title">🏗️ System Design</h2>
            <div class="content">
                <p><em>System design not yet generated.</em></p>
            </div>
        </section>
        '''
    
    design_content = system_design_data.get('content_markdown', '')
    design_html = _markdown_to_html(design_content)
    version = system_design_data.get('version', 'N/A')
    generated_by = system_design_data.get('generated_by', 'System')
    
    return f'''
    <section class="section page-break-before">
        <h2 class="section-title">🏗️ System Design (v{version})</h2>
        <p><em>Generated by: {generated_by}</em></p>
        {design_html}
    </section>
    '''


def _generate_effort_estimate_section(effort_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for effort estimate section."""
    if not effort_data:
        return '''
        <div class="financial-subsection">
            <h3>💼 Effort Estimate</h3>
            <p><em>Effort estimate not yet available.</em></p>
        </div>
        '''
    
    total_hours = effort_data.get('total_hours', 0)
    duration_weeks = effort_data.get('estimated_duration_weeks', 0)
    complexity = effort_data.get('complexity_assessment', 'N/A')
    roles = effort_data.get('roles', [])
    
    roles_html = '<table class="data-table"><tr><th>Role</th><th>Hours</th></tr>'
    for role in roles:
        role_name = role.get('role', 'Unknown')
        hours = role.get('hours', 0)
        roles_html += f'<tr><td>{role_name}</td><td>{hours}</td></tr>'
    roles_html += '</table>'
    
    return f'''
    <div class="financial-subsection">
        <h3>💼 Effort Estimate</h3>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-label">Total Hours</div>
                <div class="metric-value">{total_hours:,}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{duration_weeks} weeks</div>
            </div>
        </div>
        <p><strong>Complexity:</strong> {complexity}</p>
        <h4>Role Breakdown:</h4>
        {roles_html}
    </div>
    '''


def _generate_cost_estimate_section(cost_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for cost estimate section."""
    if not cost_data:
        return '''
        <div class="financial-subsection">
            <h3>💰 Cost Estimate</h3>
            <p><em>Cost estimate not yet available.</em></p>
        </div>
        '''
    
    estimated_cost = cost_data.get('estimated_cost', 0)
    currency = cost_data.get('currency', 'USD')
    rate_card_used = cost_data.get('rate_card_used', 'N/A')
    breakdown = cost_data.get('breakdown_by_role', [])
    
    breakdown_html = '<table class="data-table"><tr><th>Role</th><th>Hours</th><th>Rate</th><th>Cost</th></tr>'
    for item in breakdown:
        role = item.get('role', 'Unknown')
        hours = item.get('hours', 0)
        rate = item.get('hourly_rate', 0)
        cost = item.get('total_cost', 0)
        breakdown_html += f'<tr><td>{role}</td><td>{hours}</td><td>${rate:,.2f}</td><td>${cost:,.2f}</td></tr>'
    breakdown_html += '</table>'
    
    return f'''
    <div class="financial-subsection">
        <h3>💰 Cost Estimate</h3>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value currency-amount">${estimated_cost:,.2f} {currency}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Rate Card</div>
                <div class="metric-value">{rate_card_used}</div>
            </div>
        </div>
        <h4>Cost Breakdown:</h4>
        {breakdown_html}
    </div>
    '''


def _generate_value_projection_section(value_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for value projection section."""
    if not value_data:
        return '''
        <div class="financial-subsection">
            <h3>📈 Value Projection</h3>
            <p><em>Value projection not yet available.</em></p>
        </div>
        '''
    
    scenarios = value_data.get('scenarios', [])
    currency = value_data.get('currency', 'USD')
    methodology = value_data.get('methodology', 'N/A')
    
    scenarios_html = '<table class="data-table"><tr><th>Scenario</th><th>Value</th><th>Description</th></tr>'
    for scenario in scenarios:
        case = scenario.get('case', 'Unknown')
        value = scenario.get('value', 0)
        description = scenario.get('description', '')
        scenarios_html += f'<tr><td>{case}</td><td>${value:,.2f}</td><td>{description}</td></tr>'
    scenarios_html += '</table>'
    
    return f'''
    <div class="financial-subsection">
        <h3>📈 Value Projection</h3>
        <p><strong>Methodology:</strong> {methodology}</p>
        <h4>Value Scenarios:</h4>
        {scenarios_html}
    </div>
    '''


def _generate_financial_summary_section(financial_data: Optional[Dict[str, Any]]) -> str:
    """Generate HTML for financial summary section."""
    if not financial_data:
        return '''
        <div class="financial-subsection">
            <h3>📊 Financial Summary</h3>
            <p><em>Financial summary not yet available.</em></p>
        </div>
        '''
    
    total_cost = financial_data.get('total_estimated_cost', 0)
    currency = financial_data.get('currency', 'USD')
    value_scenarios = financial_data.get('value_scenarios', {})
    metrics = financial_data.get('financial_metrics', {})
    
    primary_net_value = metrics.get('primary_net_value', 0)
    primary_roi = metrics.get('primary_roi_percentage', 'N/A')
    payback_period = metrics.get('simple_payback_period_years', 'N/A')
    
    scenarios_html = ''
    for scenario, value in value_scenarios.items():
        net_value = value - total_cost
        scenarios_html += f'''
        <div class="metric-item">
            <div class="metric-label">{scenario} Scenario</div>
            <div class="metric-value currency-amount">${value:,.2f}</div>
            <div style="font-size: 9pt; color: #666;">Net: ${net_value:,.2f}</div>
        </div>
        '''
    
    return f'''
    <div class="financial-subsection">
        <h3>📊 Financial Summary</h3>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-label">Total Investment</div>
                <div class="metric-value currency-amount">${total_cost:,.2f} {currency}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Primary Net Value</div>
                <div class="metric-value currency-amount">${primary_net_value:,.2f}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Primary ROI</div>
                <div class="metric-value">{primary_roi}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Payback Period</div>
                <div class="metric-value">{payback_period}</div>
            </div>
        </div>
        <h4>Value Scenarios:</h4>
        <div class="metric-grid">
            {scenarios_html}
        </div>
    </div>
    '''


def _generate_approval_history_section(history: list) -> str:
    """Generate HTML for approval history section."""
    if not history:
        return '''
        <section class="section">
            <h2 class="section-title">📝 History</h2>
            <div class="content">
                <p><em>No history available.</em></p>
            </div>
        </section>
        '''
    
    history_html = '<table class="data-table"><tr><th>Date</th><th>Source</th><th>Type</th><th>Content</th></tr>'
    for item in history:
        timestamp = _format_datetime(item.get('timestamp'))
        source = item.get('source', 'SYSTEM')
        message_type = item.get('messageType', 'UPDATE')
        content = str(item.get('content', ''))[:100] + '...' if len(str(item.get('content', ''))) > 100 else str(item.get('content', ''))
        history_html += f'<tr><td>{timestamp}</td><td>{source}</td><td>{message_type}</td><td>{content}</td></tr>'
    history_html += '</table>'
    
    return f'''
    <section class="section">
        <h2 class="section-title">📝 Approval History</h2>
        {history_html}
    </section>
    ''' 