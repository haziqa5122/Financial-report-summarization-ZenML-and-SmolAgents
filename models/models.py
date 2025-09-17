from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class DocumentSections(BaseModel):
    management_discussion: str
    risk_factors: str
    financial_statements: str

class DocumentMetadata(BaseModel):
    company_name: str
    sector: str
    fiscal_year: str

class FinancialMetrics(BaseModel):
    """Pydantic model for financial metrics extraction."""
    revenue: Optional[str] = Field(None, description="Company revenue (e.g., '$1098.7 million')")
    gross_profit_margin: Optional[str] = Field(None, description="Gross profit margin percentage (e.g., '30.04%')")
    net_profit_margin: Optional[str] = Field(None, description="Net profit margin percentage (e.g., '0.43%')")
    debt_to_equity_ratio: Optional[str] = Field(None, description="Debt to equity ratio (e.g., '3.44')")
    total_debt_ratio: Optional[str] = Field(None, description="Total debt ratio (e.g., '1.00')")
    current_ratio: Optional[str] = Field(None, description="Current ratio if available")
    return_on_equity: Optional[str] = Field(None, description="Return on equity if available")
    return_on_assets: Optional[str] = Field(None, description="Return on assets if available")


class ExtractedData(BaseModel):
    """Complete structure for extracted business analysis data."""
    metrics: FinancialMetrics = Field(default_factory=FinancialMetrics, description="Financial metrics extracted from the analysis")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information and company insights")
    competitor: str = Field(default="", description="Competitor analysis and market landscape information")
    contradictions: str = Field(default="", description="Any contradictions, validation needs, or analytical gaps identified")
    additional_context: str = Field(default="", description="Additional context or recommendations")

