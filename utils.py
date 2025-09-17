from typing import Dict, Any
import json
from litellm import completion
import os
import re
import ast
from models.models import ExtractedData
from config.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT

def extract_metrics(response: Dict[str, Any], model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Extract financial metrics and insights using LiteLLM with Pydantic structured output.
    
    Args:
        response: A structured dictionary containing task outcomes and context.
        model: The LLM model to use for extraction
        
    Returns:
        A dictionary containing extracted financial metrics and relevant insights.
    """
    input_text = prepare_input_text(response)
    
    # Create the extraction prompt
    
    try:
        # Make the LLM call with structured output
        response_obj = completion(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": EXTRACTION_USER_PROMPT.format(input_text = input_text)}
            ],
            response_format=ExtractedData,
            temperature=0.1  # Low temperature for consistent extraction
        )
        
        # Parse the structured response
        extracted_data = json.loads(response_obj.choices[0].message.content)
        
        # Convert Pydantic model format to your expected format
        formatted_result = {
            "metrics": {
                k.replace('_', ' ').title(): v 
                for k, v in extracted_data["metrics"].items() 
                if v is not None
            },
            "context": extracted_data.get("context", {}),
            "competitor": extracted_data.get("competitor", ""),
            "contradictions": extracted_data.get("contradictions", ""),
            "additional_context": extracted_data.get("additional_context", "")
        }
        
        return formatted_result
        
    except Exception as e:
        print(f"Error in LLM extraction: {e}")
        # Fallback to simple extraction
        return fallback_extraction(response)

def generate_metrics_html(metrics: Dict[str, str]) -> str:
    """
    Generate clean HTML for financial metrics display.
    
    Args:
        metrics: Dictionary of extracted financial metrics.
        
    Returns:
        HTML string with styled metrics display.
    """
    if not metrics:
        return '<div class="no-metrics"><p>No financial metrics available.</p></div>'
    
    html = '''
    <style>
    .metrics-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        max-width: 800px;
        margin: 20px auto;
        padding: 20px;
    }
    .metrics-header {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 20px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 15px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .no-metrics {
        text-align: center;
        padding: 40px;
        color: #7f8c8d;
        font-style: italic;
    }
    </style>
    
    <div class="metrics-container">
        <div class="metrics-header">Financial Metrics</div>
        <div class="metrics-grid">
    '''
    
    for metric, value in metrics.items():
        html += f'''
        <div class="metric-card">
            <div class="metric-label">{metric}</div>
            <div class="metric-value">{value}</div>
        </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def prepare_input_text(response: Dict[str, Any]) -> str:
    """
    Prepare the input text from the response dictionary for LLM processing.
    
    Args:
        response: The original response dictionary
        
    Returns:
        Formatted text string for LLM analysis
    """
    text_parts = []
    
    # Add short version
    short_version = response.get("1. Task outcome (short version)", "")
    if short_version:
        text_parts.append(f"SUMMARY: {short_version}")
    
    # Add detailed version
    detailed_outcome = response.get("2. Task outcome (extremely detailed version)", {})
    if detailed_outcome:
        text_parts.append("DETAILED ANALYSIS:")
        if isinstance(detailed_outcome, dict):
            for key, value in detailed_outcome.items():
                text_parts.append(f"{key}: {value}")
        else:
            text_parts.append(str(detailed_outcome))
    
    # Add additional context
    additional_context = response.get("3. Additional context (if relevant)", "")
    if additional_context:
        text_parts.append(f"ADDITIONAL CONTEXT: {additional_context}")
    
    return "\n\n".join(text_parts)


def fallback_extraction(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple fallback extraction if LLM approach fails.
    
    Args:
        response: Original response dictionary
        
    Returns:
        Basic extracted data structure
    """
    extracted_data = {
        "metrics": {},
        "context": {},
        "competitor": "",
        "contradictions": "",
        "additional_context": ""
    }
    
    detailed_outcome = response.get("2. Task outcome (extremely detailed version)", {})
    
    if isinstance(detailed_outcome, dict):
        extracted_data["context"] = detailed_outcome
        
        # Extract from Financial Metrics section if available
        financial_text = detailed_outcome.get("Financial Metrics", "")
        if financial_text:
            # Simple pattern matching as fallback
            import re
            
            patterns = {
                "Revenue": r'\$?([\d,\.]+)\s*million',
                "Gross Profit Margin": r'Gross Profit Margin.*?([\d\.]+)%',
                "Net Profit Margin": r'Net Profit Margin.*?([\d\.]+)%',
                "Debt To Equity Ratio": r'Debt to Equity Ratio.*?([\d\.]+)',
                "Total Debt Ratio": r'Total Debt Ratio.*?([\d\.]+)'
            }
            
            for metric, pattern in patterns.items():
                match = re.search(pattern, financial_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    if metric == "Revenue":
                        extracted_data["metrics"][metric] = f"${value} million"
                    elif "Margin" in metric:
                        extracted_data["metrics"][metric] = f"{value}%"
                    else:
                        extracted_data["metrics"][metric] = value
        
        # Extract competitor info
        extracted_data["competitor"] = detailed_outcome.get("Competitor Analysis", "")
        
        # Extract contradictions
        extracted_data["contradictions"] = detailed_outcome.get("Contradictory Analysis", "")
    
    extracted_data["additional_context"] = response.get("3. Additional context (if relevant)", "")
    
    return extracted_data

def string_to_dict(input_str):
    try:
        input_str = input_str.replace("Here is the final answer from your managed agent 'None':", "").strip()
        return ast.literal_eval(input_str)
    except (SyntaxError, ValueError) as e:
        print(f"Error converting string to dict: {e}")
        return None

def generate_context_html(context: Dict[str, Any]) -> str:
    """
    Converts context dictionary to structured HTML with modern styling.

    Args:
        context: A dictionary containing contextual information from the analysis.

    Returns:
        A string containing HTML content with styling.
    """
    if not context:
        return '<div class="no-context"><p>No context available.</p></div>'

    html = '''
    <style>
    .context-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        max-width: 900px;
        margin: 20px auto;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .context-header {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 25px;
        border-bottom: 3px solid #e74c3c;
        padding-bottom: 10px;
    }
    .context-section {
        margin-bottom: 25px;
        background: white;
        border-radius: 8px;
        padding: 20px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .section-title {
        color: #e74c3c;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .section-content {
        color: #2c3e50;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .context-list {
        margin: 10px 0;
        padding-left: 0;
    }
    .context-list li {
        list-style: none;
        padding: 8px 0;
        border-bottom: 1px solid #ecf0f1;
        position: relative;
        padding-left: 20px;
    }
    .context-list li:before {
        content: "▸";
        color: #3498db;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    .context-list li:last-child {
        border-bottom: none;
    }
    .no-context {
        text-align: center;
        padding: 40px;
        color: #7f8c8d;
        font-style: italic;
    }
    </style>
    
    <div class="context-container">
        <div class="context-header">Business Analysis Context</div>
    '''

    # Handle different types of context input
    if isinstance(context, dict):
        for section_key, section_value in context.items():
            if section_value:  # Only show non-empty sections
                html += f'''
                <div class="context-section">
                    <div class="section-title">{section_key.replace('_', ' ')}</div>
                    <div class="section-content">
                '''
                
                if isinstance(section_value, str):
                    # Handle string values - convert to proper HTML
                    content = format_text_content(section_value)
                    html += content
                elif isinstance(section_value, (list, tuple)):
                    # Handle list values
                    html += '<ul class="context-list">'
                    for item in section_value:
                        html += f'<li>{str(item)}</li>'
                    html += '</ul>'
                elif isinstance(section_value, dict):
                    # Handle nested dictionary values
                    for sub_key, sub_value in section_value.items():
                        html += f'<p><strong>{sub_key}:</strong> {str(sub_value)}</p>'
                else:
                    html += f'<p>{str(section_value)}</p>'
                
                html += '''
                    </div>
                </div>
                '''
    
    elif isinstance(context, str):
        # Handle legacy string format
        html += f'''
        <div class="context-section">
            <div class="section-content">
                {format_text_content(context)}
            </div>
        </div>
        '''
    
    html += '</div>'
    return html


def format_text_content(text: str) -> str:
    """
    Format text content with basic markdown-like parsing.
    
    Args:
        text: Raw text content
        
    Returns:
        Formatted HTML content
    """
    if not text:
        return "<p>No content available.</p>"
    
    html_parts = []
    in_ul = in_ol = False
    
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        
        if not line:
            # Close any open lists on blank lines
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            if in_ol:
                html_parts.append("</ol>")
                in_ol = False
            continue
        
        if line.startswith("### "):
            html_parts.append(f"<h4>{line[4:].strip()}</h4>")
        elif line.startswith("#### "):
            html_parts.append(f"<h5>{line[5:].strip()}</h5>")
        elif re.match(r"- ", line):
            if not in_ul:
                html_parts.append('<ul class="context-list">')
                in_ul = True
            html_parts.append(f"<li>{line[2:].strip()}</li>")
        elif re.match(r"\d+\.", line):
            if not in_ol:
                html_parts.append('<ol class="context-list">')
                in_ol = True
            html_parts.append(f"<li>{line[line.find('.') + 1:].strip()}</li>")
        else:
            html_parts.append(f"<p>{line}</p>")
    
    # Close any unclosed lists
    if in_ul:
        html_parts.append("</ul>")
    if in_ol:
        html_parts.append("</ol>")
    
    return "\n".join(html_parts)
