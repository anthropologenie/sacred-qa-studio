"""
AGQ (Aspirational Gravity Quotient) Calculator v1.0

Philosophy: Technical quality × Values alignment = True marketing excellence

Scoring: 0.0 to 5.0 (like credit scores, higher is better)
- 0.0-2.0: Critical misalignment (red flag)
- 2.1-3.5: Needs improvement (amber)
- 3.6-4.5: Good alignment (green)
- 4.6-5.0: Exceptional (gold standard)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """A single test finding"""
    category: str  # "forms", "ga4", "ads", "perf", "a11y"
    severity: Severity
    title: str
    description: str
    evidence_url: Optional[str] = None
    values_impact: float = 0.0  # 0.0 to 1.0 (how much this impacts values alignment)


@dataclass
class ClientValues:
    """Client's stated values from intake form"""
    accessibility_commitment: bool = False  # "We commit to WCAG AA"
    privacy_conscious: bool = False  # "We respect user privacy"
    transparency: bool = False  # "We're transparent about data use"
    performance_matters: bool = False  # "Fast UX is important to us"
    mobile_first: bool = False  # "Mobile users are our priority"
    
    # Free-form values statement
    values_statement: Optional[str] = None


@dataclass
class AGQScore:
    """Complete AGQ assessment"""
    overall_score: float  # 0.0 to 5.0
    technical_score: float  # 0.0 to 5.0
    values_score: float  # 0.0 to 5.0
    breakdown: Dict[str, float]  # Category-level scores
    findings_by_severity: Dict[str, int]
    values_gaps: List[str]  # Specific misalignments
    recommendations: List[str]


class AGQCalculator:
    """
    AGQ Calculation Engine
    
    Formula: AGQ = (Technical Quality × 0.6) + (Values Alignment × 0.4)
    
    Why 60/40?
    - Technical quality is table stakes (must work)
    - Values alignment differentiates (who you are)
    """
    
    # Category weights (sum to 1.0)
    CATEGORY_WEIGHTS = {
        "forms": 0.30,      # Most critical - conversion depends on this
        "ga4": 0.20,        # Data integrity matters
        "ads": 0.15,        # Money on the line
        "perf": 0.20,       # UX impact
        "a11y": 0.15,       # Values signal
    }
    
    # Severity penalties (subtracted from max score)
    SEVERITY_PENALTIES = {
        Severity.CRITICAL: 1.5,  # Massive impact
        Severity.HIGH: 0.8,
        Severity.MEDIUM: 0.3,
        Severity.LOW: 0.1,
        Severity.INFO: 0.0,
    }
    
    def calculate(
        self,
        findings: List[Finding],
        client_values: ClientValues,
    ) -> AGQScore:
        """Calculate AGQ score from test findings and client values"""
        
        # Step 1: Calculate technical quality score (0-5)
        technical_score = self._calculate_technical_score(findings)
        
        # Step 2: Calculate values alignment score (0-5)
        values_score = self._calculate_values_score(findings, client_values)
        
        # Step 3: Combine with weighting
        overall_score = (technical_score * 0.6) + (values_score * 0.4)
        
        # Step 4: Generate breakdown
        breakdown = self._calculate_category_breakdown(findings)
        
        # Step 5: Identify values gaps
        values_gaps = self._identify_values_gaps(findings, client_values)
        
        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(
            technical_score,
            values_score,
            values_gaps
        )
        
        # Step 7: Count findings by severity
        findings_by_severity = self._count_by_severity(findings)
        
        return AGQScore(
            overall_score=round(overall_score, 1),
            technical_score=round(technical_score, 1),
            values_score=round(values_score, 1),
            breakdown=breakdown,
            findings_by_severity=findings_by_severity,
            values_gaps=values_gaps,
            recommendations=recommendations,
        )
    
    def _calculate_technical_score(self, findings: List[Finding]) -> float:
        """
        Technical score: Start at 5.0, subtract penalties
        
        Each category starts perfect, issues deduct points
        """
        category_scores = {}
        
        for category, weight in self.CATEGORY_WEIGHTS.items():
            # Start perfect
            base_score = 5.0
            
            # Find all findings for this category
            category_findings = [f for f in findings if f.category == category]
            
            # Subtract penalties
            total_penalty = sum(
                self.SEVERITY_PENALTIES[f.severity]
                for f in category_findings
            )
            
            # Don't go below 0
            category_score = max(0.0, base_score - total_penalty)
            category_scores[category] = category_score
        
        # Weighted average
        technical_score = sum(
            score * self.CATEGORY_WEIGHTS[cat]
            for cat, score in category_scores.items()
        )
        
        return min(5.0, technical_score)
    
    def _calculate_values_score(
        self,
        findings: List[Finding],
        client_values: ClientValues,
    ) -> float:
        """
        Values alignment: How well does execution match stated values?
        
        Start at 5.0, deduct for each values misalignment
        """
        values_score = 5.0
        
        # Check accessibility commitment
        if client_values.accessibility_commitment:
            a11y_criticals = [
                f for f in findings
                if f.category == "a11y" and f.severity == Severity.CRITICAL
            ]
            if a11y_criticals:
                # Critical a11y issues when committed to accessibility
                values_score -= 2.0 * len(a11y_criticals)
        
        # Check privacy consciousness
        if client_values.privacy_conscious:
            # Look for privacy-related GA4 issues
            privacy_issues = [
                f for f in findings
                if f.category == "ga4" and "privacy" in f.description.lower()
            ]
            if privacy_issues:
                values_score -= 1.5 * len(privacy_issues)
        
        # Check performance commitment
        if client_values.performance_matters:
            perf_criticals = [
                f for f in findings
                if f.category == "perf" and f.severity in [Severity.CRITICAL, Severity.HIGH]
            ]
            if perf_criticals:
                values_score -= 1.0 * len(perf_criticals)
        
        # Check mobile-first claim
        if client_values.mobile_first:
            # Look for mobile-specific issues
            mobile_issues = [
                f for f in findings
                if "mobile" in f.description.lower() and f.severity in [Severity.CRITICAL, Severity.HIGH]
            ]
            if mobile_issues:
                values_score -= 1.5 * len(mobile_issues)
        
        # Apply values_impact from individual findings
        values_deductions = sum(
            f.values_impact * self.SEVERITY_PENALTIES[f.severity]
            for f in findings
        )
        values_score -= values_deductions
        
        return max(0.0, min(5.0, values_score))
    
    def _calculate_category_breakdown(self, findings: List[Finding]) -> Dict[str, float]:
        """Category-level scores for dashboard visualization"""
        breakdown = {}
        
        for category in self.CATEGORY_WEIGHTS.keys():
            base_score = 5.0
            category_findings = [f for f in findings if f.category == category]
            
            total_penalty = sum(
                self.SEVERITY_PENALTIES[f.severity]
                for f in category_findings
            )
            
            breakdown[category] = round(max(0.0, base_score - total_penalty), 1)
        
        return breakdown
    
    def _identify_values_gaps(
        self,
        findings: List[Finding],
        client_values: ClientValues,
    ) -> List[str]:
        """Specific values misalignments to highlight in report"""
        gaps = []
        
        if client_values.accessibility_commitment:
            a11y_issues = [f for f in findings if f.category == "a11y"]
            if a11y_issues:
                gaps.append(
                    f"Accessibility commitment stated, but {len(a11y_issues)} issues found"
                )
        
        if client_values.privacy_conscious:
            # Check for excessive tracking
            tracking_findings = [
                f for f in findings
                if "tracking" in f.description.lower() or "pixel" in f.description.lower()
            ]
            if tracking_findings:
                gaps.append("Privacy consciousness stated, but tracking concerns found")
        
        if client_values.performance_matters:
            slow_pages = [
                f for f in findings
                if f.category == "perf" and "slow" in f.description.lower()
            ]
            if slow_pages:
                gaps.append("Performance stated as priority, but slow page loads detected")
        
        if client_values.mobile_first:
            mobile_issues = [
                f for f in findings
                if "mobile" in f.description.lower()
            ]
            if mobile_issues:
                gaps.append("Mobile-first claim, but mobile UX issues found")
        
        return gaps
    
    def _generate_recommendations(
        self,
        technical_score: float,
        values_score: float,
        values_gaps: List[str],
    ) -> List[str]:
        """Actionable recommendations based on scores"""
        recommendations = []
        
        if technical_score < 3.0:
            recommendations.append(
                "🔴 CRITICAL: Address technical issues immediately before scaling spend"
            )
        elif technical_score < 4.0:
            recommendations.append(
                "🟡 PRIORITY: Fix high-severity technical issues this sprint"
            )
        
        if values_score < 3.0:
            recommendations.append(
                "🔴 VALUES GAP: Significant misalignment between stated values and execution"
            )
        elif values_score < 4.0:
            recommendations.append(
                "🟡 ALIGNMENT OPPORTUNITY: Strengthen values consistency in implementation"
            )
        
        if values_gaps:
            recommendations.append(
                f"⚠️ TRANSPARENCY: Consider updating marketing claims or fixing {len(values_gaps)} gaps"
            )
        
        if technical_score > 4.0 and values_score > 4.0:
            recommendations.append(
                "✅ STRONG FOUNDATION: Maintain quality and consider case study"
            )
        
        return recommendations
    
    def _count_by_severity(self, findings: List[Finding]) -> Dict[str, int]:
        """Count findings by severity for reporting"""
        counts = {s.value: 0 for s in Severity}
        
        for finding in findings:
            counts[finding.severity.value] += 1
        
        return counts


# Example usage
if __name__ == "__main__":
    # Sample findings from test run
    findings = [
        Finding(
            category="forms",
            severity=Severity.CRITICAL,
            title="Mobile form submission fails",
            description="Form submit button unclickable on iOS Safari",
            values_impact=0.5,  # Half impact since mobile-first was claimed
        ),
        Finding(
            category="ga4",
            severity=Severity.HIGH,
            title="Conversion event missing",
            description="Purchase event not firing on checkout",
            values_impact=0.0,
        ),
        Finding(
            category="perf",
            severity=Severity.MEDIUM,
            title="LCP exceeds 2.5s",
            description="Landing page loads in 3.2s on 3G",
            values_impact=0.3,  # Some impact if performance claimed
        ),
        Finding(
            category="a11y",
            severity=Severity.HIGH,
            title="Missing alt text on hero image",
            description="Main CTA image lacks screen reader support",
            values_impact=0.8,  # High impact if accessibility committed
        ),
    ]
    
    # Client's stated values
    values = ClientValues(
        accessibility_commitment=True,
        mobile_first=True,
        performance_matters=True,
    )
    
    # Calculate AGQ
    calculator = AGQCalculator()
    score = calculator.calculate(findings, values)
    
    # Print results
    print(f"\n🎯 AGQ Score: {score.overall_score}/5.0")
    print(f"   Technical: {score.technical_score}/5.0")
    print(f"   Values: {score.values_score}/5.0")
    print(f"\n📊 Category Breakdown:")
    for cat, s in score.breakdown.items():
        print(f"   {cat}: {s}/5.0")
    print(f"\n⚠️ Findings by Severity:")
    for sev, count in score.findings_by_severity.items():
        if count > 0:
            print(f"   {sev}: {count}")
    print(f"\n🔍 Values Gaps:")
    for gap in score.values_gaps:
        print(f"   • {gap}")
    print(f"\n💡 Recommendations:")
    for rec in score.recommendations:
        print(f"   {rec}")
