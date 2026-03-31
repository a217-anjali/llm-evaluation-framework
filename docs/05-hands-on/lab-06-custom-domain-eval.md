# Lab 06: Designing a Custom Domain Evaluation

**Difficulty:** Red (Advanced)
**Duration:** 120 minutes
**Tools:** Python 3.10+, llm_eval_framework, OpenAI API, Anthropic API, Google API
**Prerequisites:** Completion of Labs 01-04, familiarity with LLM APIs

## Overview

In this advanced lab, you will design and implement a production-grade evaluation framework for legal contract review—a complex domain requiring high accuracy, completeness, citation precision, and risk identification. You'll engineer a multi-dimensional rubric, curate 30 diverse test cases, build an automated scorer with confidence intervals, run comparative evaluation against 3 models, and apply statistical significance testing.

## Learning Objectives

By the end of this lab, you will:

1. **Design domain-specific evaluation rubrics** with multiple weighted dimensions
2. **Engineer reliable test case curation** with diverse coverage and difficulty calibration
3. **Implement automated scorers** with detailed annotation schemes
4. **Run comparative model evaluation** with reproducible results
5. **Conduct statistical significance testing** to determine meaningful differences
6. **Interpret results** in production context with confidence intervals

## Part 1: Define Evaluation Scope and Requirements

### 1.1 Domain Analysis

Legal contract review is a high-stakes task requiring:
- **Accuracy:** Correctly identifying contract terms and obligations
- **Completeness:** Not missing critical clauses or risks
- **Citation:** Referencing exact contract sections (liability for hallucinations)
- **Risk Identification:** Flagging unusual, unfavorable, or concerning provisions

Create a new Python file:

```python
# legal_eval_scope.py
"""
Domain analysis for legal contract evaluation.
Defines scope, constraints, and evaluation dimensions.
"""

from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class EvaluationDimension:
    name: str
    description: str
    weight: float
    min_score: int
    max_score: int
    examples: List[str]

def define_legal_domain() -> Dict:
    """Define the legal contract review evaluation domain."""

    domain = {
        "task_description": "Review a commercial contract and provide analysis",
        "input_format": "Full contract text (1000-5000 words)",
        "expected_output": {
            "key_terms_summary": "List of critical commercial terms with values",
            "obligations": "Party-by-party obligations and deadlines",
            "risk_flags": "Identified risks with severity levels",
            "missing_provisions": "Recommendations for additions",
            "section_references": "Citations to contract sections"
        },
        "evaluation_constraints": {
            "hallucination_penalty": 0.15,  # Penalty for referencing non-existent sections
            "omission_penalty": 0.10,  # Penalty per critical term missed
            "max_output_tokens": 2000,
            "max_latency_seconds": 30
        }
    }

    return domain

def define_evaluation_dimensions() -> List[EvaluationDimension]:
    """Define the four evaluation dimensions."""

    dimensions = [
        EvaluationDimension(
            name="accuracy",
            description="Correctness of extracted terms, obligations, and risk assessments",
            weight=0.35,
            min_score=0,
            max_score=100,
            examples=[
                "Correctly identifies payment terms as 'Net 30'",
                "Accurately extracts warranty period as '12 months'",
                "Properly interprets liability cap as '$1M or annual fees, whichever is greater'"
            ]
        ),
        EvaluationDimension(
            name="completeness",
            description="Coverage of all critical contract provisions",
            weight=0.30,
            min_score=0,
            max_score=100,
            examples=[
                "Identifies all payment milestones",
                "Lists all warranties and disclaimers",
                "Flags all termination clauses and conditions"
            ]
        ),
        EvaluationDimension(
            name="citation",
            description="Accuracy of section references and quote attribution",
            weight=0.20,
            min_score=0,
            max_score=100,
            examples=[
                "References exist in contract: 'Section 3.2' is valid",
                "Quotes match exactly from contract source",
                "No references to non-existent sections or fabricated quotes"
            ]
        ),
        EvaluationDimension(
            name="risk_identification",
            description="Quality and appropriateness of risk flagging",
            weight=0.15,
            min_score=0,
            max_score=100,
            examples=[
                "Identifies unusual liability limitations",
                "Flags ambiguous or contradictory language",
                "Notes missing standard protections"
            ]
        )
    ]

    return dimensions

def define_test_case_difficulty_levels() -> Dict:
    """Define difficulty calibration for test cases."""

    return {
        "easy": {
            "characteristics": [
                "Short contracts (1000-1500 words)",
                "Clear standard terms",
                "Few ambiguous provisions",
                "Straightforward structure"
            ],
            "target_count": 8,
            "examples": [
                "Simple service agreement",
                "Standard NDA",
                "Basic equipment lease"
            ]
        },
        "medium": {
            "characteristics": [
                "Medium contracts (1500-3000 words)",
                "Mix of standard and custom terms",
                "Some complex provisions",
                "Multiple parties or conditions"
            ],
            "target_count": 12,
            "examples": [
                "Software license agreement",
                "Partnership agreement",
                "Vendor contract with SLA"
            ]
        },
        "hard": {
            "characteristics": [
                "Long contracts (3000-5000 words)",
                "Many custom and non-standard terms",
                "Complex liability and indemnification",
                "Ambiguous or contradictory language",
                "Cross-references and dependencies"
            ],
            "target_count": 10,
            "examples": [
                "Enterprise software agreement",
                "M&A agreement",
                "Complex licensing agreement"
            ]
        }
    }

if __name__ == "__main__":
    domain = define_legal_domain()
    dimensions = define_evaluation_dimensions()
    difficulty = define_test_case_difficulty_levels()

    print("Domain Specification:")
    print(json.dumps(domain, indent=2))
    print("\nEvaluation Dimensions:")
    for dim in dimensions:
        print(f"\n{dim.name.upper()} (weight: {dim.weight})")
        print(f"  {dim.description}")
    print("\nDifficulty Distribution:")
    print(f"  Easy: {difficulty['easy']['target_count']}")
    print(f"  Medium: {difficulty['medium']['target_count']}")
    print(f"  Hard: {difficulty['hard']['target_count']}")
    print(f"  Total: {sum(d['target_count'] for d in difficulty.values())}")
```

## Part 2: Engineer the Evaluation Rubric

Create the detailed scoring rubric:

```python
# legal_eval_rubric.py
"""
Multi-dimensional rubric for legal contract evaluation.
"""

from typing import Dict, List, Tuple
from enum import Enum
import json

class ScoreLevel(Enum):
    EXCELLENT = 90
    GOOD = 70
    FAIR = 50
    POOR = 30
    UNACCEPTABLE = 0

def create_accuracy_rubric() -> Dict:
    """Accuracy dimension: correctness of identified terms."""

    return {
        "dimension": "accuracy",
        "definition": "Correctness of extracted terms, obligations, and risk assessments",
        "scoring_levels": {
            90: {
                "label": "Excellent",
                "criteria": [
                    "All key commercial terms extracted with zero errors",
                    "All obligations correctly attributed to correct parties",
                    "Risk assessments align with legal best practices",
                    "No factual errors or misinterpretations"
                ]
            },
            70: {
                "label": "Good",
                "criteria": [
                    "90%+ of key terms correctly extracted",
                    "Obligations mostly correctly attributed (minor confusion acceptable)",
                    "Risk assessments are reasonable (may miss some nuance)",
                    "At most 1-2 minor errors in interpretation"
                ]
            },
            50: {
                "label": "Fair",
                "criteria": [
                    "70-89% of key terms extracted",
                    "Some obligation attribution errors",
                    "Risk assessments present but lack depth",
                    "3-4 interpretation errors that don't fundamentally break analysis"
                ]
            },
            30: {
                "label": "Poor",
                "criteria": [
                    "50-69% of key terms extracted",
                    "Multiple obligation attribution errors",
                    "Risk assessments are superficial or partially incorrect",
                    "5+ interpretation errors that impact usefulness"
                ]
            },
            0: {
                "label": "Unacceptable",
                "criteria": [
                    "<50% of key terms extracted",
                    "Fundamentally incorrect obligation understanding",
                    "Severely flawed risk assessment",
                    "Cannot be relied upon for decision-making"
                ]
            }
        },
        "error_penalties": {
            "hallucinated_term": -5,  # Points deducted per fabricated term
            "wrong_party_attribution": -3,
            "misunderstood_obligation": -4,
            "incorrect_value": -2
        }
    }

def create_completeness_rubric() -> Dict:
    """Completeness dimension: coverage of critical provisions."""

    return {
        "dimension": "completeness",
        "definition": "Coverage of all critical contract provisions",
        "critical_elements": [
            "payment_terms",
            "termination_conditions",
            "warranties",
            "liability_limitations",
            "intellectual_property",
            "confidentiality",
            "governing_law",
            "dispute_resolution",
            "force_majeure",
            "renewal_terms"
        ],
        "scoring_levels": {
            90: {
                "label": "Excellent",
                "criteria": [
                    "All critical elements identified",
                    "9-10/10 critical elements covered",
                    "No important provisions omitted",
                    "Assessment includes emerging and edge-case risks"
                ]
            },
            70: {
                "label": "Good",
                "criteria": [
                    "8-9/10 critical elements covered",
                    "Only minor or obscure provisions missed",
                    "All major risks identified"
                ]
            },
            50: {
                "label": "Fair",
                "criteria": [
                    "6-7/10 critical elements covered",
                    "Some important provisions missed",
                    "Covers main risks but may miss secondary ones"
                ]
            },
            30: {
                "label": "Poor",
                "criteria": [
                    "4-5/10 critical elements covered",
                    "Multiple important provisions missed",
                    "Missing entire categories of risk"
                ]
            },
            0: {
                "label": "Unacceptable",
                "criteria": [
                    "<4/10 critical elements covered",
                    "Grossly incomplete analysis",
                    "Would miss major contractual obligations"
                ]
            }
        },
        "omission_penalty": -8  # Per critical element missed
    }

def create_citation_rubric() -> Dict:
    """Citation dimension: accuracy of section references."""

    return {
        "dimension": "citation",
        "definition": "Accuracy of section references and quote attribution",
        "scoring_levels": {
            90: {
                "label": "Excellent",
                "criteria": [
                    "All citations reference existing sections",
                    "All quotes match source text exactly",
                    "Proper section numbering and formatting",
                    "Zero hallucinated references"
                ]
            },
            70: {
                "label": "Good",
                "criteria": [
                    "95%+ citations are accurate",
                    "Quotes are accurate (minor paraphrasing acceptable)",
                    "At most 1 minor reference error",
                    "No fabricated sections"
                ]
            },
            50: {
                "label": "Fair",
                "criteria": [
                    "85-94% citation accuracy",
                    "Some quotes are paraphrased significantly",
                    "2-3 reference errors",
                    "No clearly fabricated sections but some ambiguity"
                ]
            },
            30: {
                "label": "Poor",
                "criteria": [
                    "70-84% citation accuracy",
                    "Multiple quotes are inaccurate",
                    "4+ reference errors",
                    "Possibly references one non-existent section"
                ]
            },
            0: {
                "label": "Unacceptable",
                "criteria": [
                    "<70% citation accuracy",
                    "Quotes frequently inaccurate",
                    "Multiple hallucinated sections",
                    "Cannot be trusted for compliance review"
                ]
            }
        },
        "hallucination_penalty": -15  # Per fabricated section reference
    }

def create_risk_identification_rubric() -> Dict:
    """Risk identification dimension: quality of risk flagging."""

    return {
        "dimension": "risk_identification",
        "definition": "Quality and appropriateness of risk flagging",
        "risk_categories": [
            "liability_exposure",
            "missing_protections",
            "ambiguous_language",
            "unfavorable_terms",
            "unusual_provisions",
            "compliance_risk",
            "financial_risk"
        ],
        "severity_levels": {
            "critical": {
                "description": "Could result in material business loss or legal exposure",
                "examples": [
                    "Unlimited liability clause",
                    "Missing indemnification for third-party claims",
                    "Ambiguous termination rights"
                ]
            },
            "high": {
                "description": "Could result in significant business impact",
                "examples": [
                    "Unusually broad indemnification obligation",
                    "Restrictive non-compete clause",
                    "One-sided IP ownership"
                ]
            },
            "medium": {
                "description": "Notable but manageable business impact",
                "examples": [
                    "Unclear pricing escalation terms",
                    "Weak confidentiality obligations",
                    "Ambiguous renewal conditions"
                ]
            }
        },
        "scoring_levels": {
            90: {
                "label": "Excellent",
                "criteria": [
                    "All critical risks identified and properly severity-rated",
                    "Most high risks identified",
                    "Appropriate context provided for each risk",
                    "Recommended mitigations are practical"
                ]
            },
            70: {
                "label": "Good",
                "criteria": [
                    "All critical risks identified",
                    "80%+ of high risks identified",
                    "Risk descriptions are clear",
                    "Mitigations are reasonable"
                ]
            },
            50: {
                "label": "Fair",
                "criteria": [
                    "Most critical risks identified",
                    "60-79% of high risks identified",
                    "Risk descriptions could be more specific",
                    "Some missing risk categories"
                ]
            },
            30: {
                "label": "Poor",
                "criteria": [
                    "Some critical risks missed",
                    "<60% of high risks identified",
                    "Vague risk descriptions",
                    "Missing multiple risk categories"
                ]
            },
            0: {
                "label": "Unacceptable",
                "criteria": [
                    "Critical risks missed",
                    "No meaningful risk assessment",
                    "Could cause significant business harm if relied upon"
                ]
            }
        }
    }

def get_complete_rubric() -> Dict:
    """Assemble complete multi-dimensional rubric."""

    return {
        "task": "Legal Contract Review Evaluation",
        "created": "2026-03-31",
        "version": "1.0",
        "total_points": 100,
        "dimensions": {
            "accuracy": create_accuracy_rubric(),
            "completeness": create_completeness_rubric(),
            "citation": create_citation_rubric(),
            "risk_identification": create_risk_identification_rubric()
        },
        "weighting": {
            "accuracy": 0.35,
            "completeness": 0.30,
            "citation": 0.20,
            "risk_identification": 0.15
        },
        "aggregation_method": "weighted_average",
        "passing_threshold": 65,
        "production_threshold": 80
    }

if __name__ == "__main__":
    rubric = get_complete_rubric()
    print(json.dumps(rubric, indent=2))
```

## Part 3: Curate Test Cases

Create 30 diverse test cases with varying difficulty:

```python
# legal_eval_testcases.py
"""
Test case curation for legal contract evaluation.
Includes 30 cases across difficulty levels with reference answers.
"""

from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class TestCase:
    id: str
    difficulty: str
    contract_type: str
    contract_text: str
    reference_answer: Dict
    ground_truth_metrics: Dict

def create_test_cases() -> List[TestCase]:
    """Create 30 diverse test cases."""

    test_cases = []

    # EASY CASES (8 cases)

    test_cases.append(TestCase(
        id="legal_01_easy_nda",
        difficulty="easy",
        contract_type="Non-Disclosure Agreement",
        contract_text="""
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of March 31, 2026,
between ABC Company ("Discloser") and XYZ Corporation ("Recipient").

1. CONFIDENTIAL INFORMATION
Confidential Information includes all non-public, proprietary information disclosed by
Discloser to Recipient, including technical data, business plans, customer lists, and
financial information. Confidential Information excludes information that: (a) is publicly
available through no fault of Recipient, (b) is rightfully received from third parties
without confidentiality obligations, or (c) is independently developed by Recipient.

2. OBLIGATIONS
Recipient agrees to: (a) maintain Confidential Information in strict confidence,
(b) limit disclosure to employees with a legitimate need to know, (c) apply reasonable
security measures equivalent to those used for its own confidential information, and
(d) not disclose to third parties without prior written consent.

3. TERM
This Agreement remains in effect for three (3) years from the date of disclosure,
provided that trade secrets shall remain protected under applicable law.

4. RETURN OF INFORMATION
Upon termination or request, Recipient shall return or destroy all Confidential Information
and certify such destruction in writing within thirty (30) days.

5. GOVERNING LAW
This Agreement shall be governed by the laws of New York, without regard to conflicts of law.

6. ENTIRE AGREEMENT
This Agreement constitutes the entire agreement between parties and supersedes all prior
negotiations and understandings.
        """,
        reference_answer={
            "key_terms": {
                "term_duration": "3 years from disclosure",
                "confidentiality_scope": "Non-public proprietary information",
                "governing_jurisdiction": "New York"
            },
            "party_obligations": {
                "Recipient": [
                    "Maintain strict confidentiality",
                    "Limit disclosure to employees with need-to-know",
                    "Apply reasonable security measures",
                    "Obtain written consent for third-party disclosure",
                    "Return or destroy information within 30 days upon request"
                ]
            },
            "critical_risks": [
                {
                    "risk": "Trade secret protection may be stronger than 3-year term",
                    "severity": "medium"
                }
            ],
            "missing_provisions": [
                "Permitted disclosures to legal counsel",
                "Definition of 'reasonable security measures'",
                "Remedies for breach"
            ]
        },
        ground_truth_metrics={
            "accuracy_max_score": 95,
            "completeness_coverage": 8,  # out of 10 critical elements
            "citation_accuracy": 1.0,
            "risk_count_expected": 3
        }
    ))

    # Add 7 more easy cases (abbreviated for space)
    for i in range(2, 9):
        test_cases.append(TestCase(
            id=f"legal_{i:02d}_easy",
            difficulty="easy",
            contract_type="Simple Service Agreement" if i % 2 == 0 else "Equipment Lease",
            contract_text=f"[Contract text for easy case {i}]",
            reference_answer={
                "key_terms": {"structure": "simplified"},
                "party_obligations": {"primary_party": ["obligation_1", "obligation_2"]},
                "critical_risks": [{"risk": "sample_risk", "severity": "low"}],
                "missing_provisions": []
            },
            ground_truth_metrics={
                "accuracy_max_score": 92 + i,
                "completeness_coverage": 7 + (i % 2),
                "citation_accuracy": 0.98,
                "risk_count_expected": 2
            }
        ))

    # MEDIUM CASES (12 cases)
    test_cases.append(TestCase(
        id="legal_09_medium_saas",
        difficulty="medium",
        contract_type="SaaS Agreement",
        contract_text="""
SOFTWARE AS A SERVICE AGREEMENT

This Software as a Service Agreement is entered into between TechCorp ("Provider")
and ClientCo ("Customer").

1. SERVICE DESCRIPTION
Provider shall provide cloud-based project management software ("Service") with 99.5%
uptime SLA during business hours (9AM-6PM EST, Monday-Friday).

2. TERM AND RENEWAL
Initial term is twelve (12) months from launch date. Automatically renews for additional
12-month periods unless either party provides 60 days written notice of non-renewal.

3. FEES AND PAYMENT
Annual fee: $120,000 payable quarterly in advance ($30,000 per quarter). Late payments
accrue 1.5% monthly interest. Payment is non-refundable except as specified in Section 8.

4. SERVICE LEVEL AGREEMENT
Provider guarantees 99.5% monthly uptime. Scheduled maintenance (notified 48 hours
in advance) is excluded. For each 0.1% below SLA, Customer receives service credit
of 5% monthly fee (max 30%).

5. DATA SECURITY
Provider implements SOC 2 Type II controls and 256-bit AES encryption for data at rest.
Customer is responsible for access credentials and endpoint security.

6. INTELLECTUAL PROPERTY
Customer retains all rights to Customer Data. Provider retains rights to Service and
pre-existing tools. Provider may use anonymized usage data for product improvement.

7. LIABILITY
Except for IP indemnification and confidentiality breach, Provider's liability is
capped at fees paid in the 12 months preceding the claim.

8. REFUND POLICY
Customers may request refund within 30 days of contract signing if Service has not
been used productively. No refunds after 30 days.

9. TERMINATION
Either party may terminate for material breach if not cured within 30 days of notice.
Provider may suspend Service immediately for non-payment.

10. GOVERNING LAW
This Agreement is governed by Delaware law.
        """,
        reference_answer={
            "key_terms": {
                "service_availability": "99.5% uptime SLA (business hours only)",
                "annual_cost": "$120,000 paid quarterly",
                "payment_terms": "Quarterly in advance, non-refundable except within 30 days",
                "contract_term": "12 months auto-renewing, 60-day cancellation notice",
                "liability_cap": "12 months of fees paid",
                "data_security": "SOC 2 Type II, AES-256 encryption"
            },
            "party_obligations": {
                "Provider": [
                    "Maintain 99.5% uptime during business hours",
                    "Implement SOC 2 Type II controls",
                    "Provide 48-hour notice for maintenance",
                    "Issue service credits for SLA breaches",
                    "Protect Customer Data with encryption"
                ],
                "Customer": [
                    "Pay $30,000 quarterly in advance",
                    "Maintain access credential security",
                    "Ensure endpoint security",
                    "Provide 60-day cancellation notice"
                ]
            },
            "critical_risks": [
                {
                    "risk": "SLA only covers business hours, not 24/7 production use",
                    "severity": "high"
                },
                {
                    "risk": "Unilateral Provider suspension rights for non-payment could disrupt operations",
                    "severity": "high"
                },
                {
                    "risk": "Service credits max at 30% monthly fee; may not fully compensate for downtime",
                    "severity": "medium"
                }
            ],
            "missing_provisions": [
                "Specific data breach notification timeline",
                "Customer data deletion upon termination",
                "Dispute resolution/arbitration clause",
                "Define 'used productively' for refund eligibility"
            ]
        },
        ground_truth_metrics={
            "accuracy_max_score": 88,
            "completeness_coverage": 9,
            "citation_accuracy": 0.96,
            "risk_count_expected": 5
        }
    ))

    # Add 11 more medium cases (abbreviated)
    for i in range(10, 21):
        test_cases.append(TestCase(
            id=f"legal_{i:02d}_medium",
            difficulty="medium",
            contract_type="Partnership Agreement" if i % 2 == 0 else "Vendor Contract",
            contract_text=f"[Medium difficulty contract text {i}]",
            reference_answer={
                "key_terms": {"complexity": "moderate"},
                "party_obligations": {"multiple_parties": ["obligations"]},
                "critical_risks": [{"risk": "complex_risk", "severity": "medium"}],
                "missing_provisions": ["some_typical_provisions"]
            },
            ground_truth_metrics={
                "accuracy_max_score": 85 + (i % 3),
                "completeness_coverage": 8,
                "citation_accuracy": 0.94,
                "risk_count_expected": 4
            }
        ))

    # HARD CASES (10 cases)
    test_cases.append(TestCase(
        id="legal_21_hard_maasale",
        difficulty="hard",
        contract_type="M&A Agreement",
        contract_text="""
MASTER ASSET PURCHASE AGREEMENT

This Master Asset Purchase Agreement ("Agreement") is entered into as of March 31, 2026,
between Acquirer Corp ("Buyer") and Seller Holdings LLC ("Seller").

1. PURCHASE AND SALE
Buyer shall acquire substantially all assets of Seller's business division including
tangible assets, intellectual property, customer contracts, and goodwill for the
Purchase Price.

2. PURCHASE PRICE AND EARNOUT
Base Purchase Price: $50,000,000 payable at closing via wire transfer.
Earnout: Up to $10,000,000 payable over 3 years based on achievement of:
  - Year 1: $3M if EBITDA exceeds $15M (measured Dec 31, 2026)
  - Year 2: $3.5M if EBITDA exceeds $16M (measured Dec 31, 2027)
  - Year 3: $3.5M if EBITDA exceeds $17M (measured Dec 31, 2028)
EBITDA calculated per GAAP, subject to purchase price adjustment procedures in Schedule A.

3. REPRESENTATIONS AND WARRANTIES
Seller represents and warrants:
  (a) Organization: Seller is duly organized and has full power and authority
  (b) Assets: Seller owns or has exclusive rights to all Assets
  (c) IP: All intellectual property is owned free and clear of liens; Schedule B lists
      all IP and pending applications
  (d) Contracts: All material contracts detailed in Schedule C; no breaches exist
  (e) Compliance: All operations in compliance with applicable laws
  (f) Litigation: Schedule D lists all pending and threatened litigation
  (g) Environmental: No environmental liabilities; Schedule E lists all environmental
      reports conducted
  (h) Taxes: All tax returns filed and payments made; Schedule F details tax disputes
  (i) Employees: Schedule G lists all employees; Schedule H lists pending employment claims
  (j) Financial Statements: Audited financials attached as Schedule I are accurate

4. REPRESENTATIONS AND WARRANTIES SURVIVAL
General representations survive 18 months from closing. Tax representations survive
until 60 days after statute of limitations expiration. Fundamental reps (authority,
title, IP, compliance with laws) survive for 3 years.

5. INDEMNIFICATION
Seller shall indemnify Buyer for breach of representations/warranties up to:
  - Deductible: $250,000 (no indemnification below threshold)
  - Cap: $5,000,000 (except Fundamental Reps: $10,000,000)
  - Basket: $1,000,000 annual aggregate excess over deductible
Indemnification claims must be made during survival period only.

6. EMPLOYEE MATTERS
Buyer shall assume all employment agreements listed in Schedule G. Seller shall
provide WARN Act compliance. Buyer has discretion to offer positions; terminated
employees receive severance per Schedule H.

7. ASSUMED AND RETAINED LIABILITIES
Buyer assumes identified liabilities per Schedule J. Seller retains all other
liabilities, including pending and threatened claims arising before closing.

8. MATERIAL ADVERSE CHANGE
If Material Adverse Change occurs between signing and closing, either party may
terminate. MAC is defined as material adverse effect on business, excluding general
economic conditions and industry-wide effects.

9. CLOSING CONDITIONS
Conditions include: (a) accuracy of representations and warranties, (b) compliance
with covenants, (c) third-party and regulatory approvals, (d) no material litigation
preventing closing, (e) delivery of closing documents.

10. CONDUCT BETWEEN SIGNING AND CLOSING
Seller shall operate in ordinary course, maintain assets, and not without Buyer consent:
(a) incur debt >$100K, (b) enter contracts >$250K, (c) sell or dispose of assets >$50K,
(d) grant liens, (e) declare dividends, (f) accelerate revenue collection.

11. INDEMNIFICATION PROCEDURES
Notice of claim within 30 days. Indemnified party shall cooperate in defense.
Settlements require written consent (not unreasonably withheld).

12. TAX ALLOCATION
Allocation of purchase price per Section 1060 shall be prepared by Buyer and provided
to Seller within 90 days of closing. Seller has 30 days to approve or submit alternative
allocation. Good faith negotiation required; IRS filing per agreed allocation.

13. TERMINATION
Agreement may be terminated if: (a) closing hasn't occurred by December 31, 2026
(outside closing party's control), (b) governmental authority prohibits transaction,
(c) either party materially breaches unresolved over 30-day cure period. Termination
rights are exclusive remedy unless fraud or willful breach.

14. CONFIDENTIALITY
Both parties shall maintain confidentiality except for filings with SEC, lenders,
and as required by law. Confidentiality survives termination indefinitely except
publicly disclosed information.

15. DISPUTE RESOLUTION
Any disputes shall be subject to binding arbitration under JAMS rules, seated in
New York, with one arbitrator for claims <$5M, three for larger claims. Prevailing
party recovers reasonable attorney fees and costs.

16. GOVERNING LAW AND JURISDICTION
This Agreement is governed by Delaware law. Venue is proper in Delaware Court of
Chancery. Parties waive jury trial.

17. AMENDMENTS AND WAIVERS
Amendments must be in writing signed by both parties. No waiver of one breach
constitutes waiver of other breaches.

18. SCHEDULES AND EXHIBITS
The following schedules are material and attached:
  - Schedule A: Purchase Price Adjustment Procedures
  - Schedule B: Intellectual Property
  - Schedule C: Material Contracts
  - Schedule D: Litigation
  - Schedule E: Environmental Reports
  - Schedule F: Tax Matters
  - Schedule G: Employees
  - Schedule H: Severance Arrangements
  - Schedule I: Audited Financial Statements
  - Schedule J: Assumed Liabilities
        """,
        reference_answer={
            "key_terms": {
                "base_purchase_price": "$50,000,000 at closing",
                "earnout_structure": "$10,000,000 over 3 years tied to EBITDA milestones",
                "earnout_targets": {
                    "year_1": "$3M if EBITDA > $15M",
                    "year_2": "$3.5M if EBITDA > $16M",
                    "year_3": "$3.5M if EBITDA > $17M"
                },
                "indemnification_cap": "$5,000,000 general (Fundamental Reps: $10,000,000)",
                "indemnification_deductible": "$250,000 basket threshold",
                "rep_survival_periods": {
                    "general": "18 months",
                    "tax": "60 days after statute expiration",
                    "fundamental": "3 years"
                },
                "closing_deadline": "December 31, 2026",
                "arbitration_venue": "New York, JAMS"
            },
            "party_obligations": {
                "Seller": [
                    "Transfer all Assets free and clear of liens",
                    "Indemnify Buyer for breaches up to cap",
                    "Provide accurate representations through closing",
                    "Maintain operations in ordinary course",
                    "Obtain third-party consents",
                    "Provide WARN Act compliance",
                    "Allocate purchase price per Section 1060"
                ],
                "Buyer": [
                    "Pay base purchase price at closing via wire",
                    "Pay earnout if milestones achieved (Buyer certifies EBITDA)",
                    "Assume identified liabilities per Schedule J",
                    "Offer positions to identified employees",
                    "Close by December 31, 2026 or waive deadline"
                ]
            },
            "critical_risks": [
                {
                    "risk": "Earnout tied to EBITDA but defined by Buyer; creates incentive misalignment",
                    "severity": "critical"
                },
                {
                    "risk": "Seller retains undefined 'pending and threatened claims' creating unbounded liability",
                    "severity": "critical"
                },
                {
                    "risk": "Material Adverse Change definition is vague; disputes likely over termination rights",
                    "severity": "critical"
                },
                {
                    "risk": "Survival periods vary widely; Seller has tail exposure for 3 years",
                    "severity": "high"
                },
                {
                    "risk": "Buyer has unilateral discretion to offer/not offer employee positions, affecting severance obligations",
                    "severity": "high"
                }
            ],
            "missing_provisions": [
                "Definition of Material Adverse Change with specific thresholds",
                "Post-closing transition period and service obligations",
                "Non-compete and non-solicitation provisions for Seller executives",
                "Cure procedures for indemnifiable breaches",
                "Insurance requirements during earnout period",
                "Mechanics for earnout dispute resolution separate from other disputes"
            ]
        },
        ground_truth_metrics={
            "accuracy_max_score": 78,
            "completeness_coverage": 10,
            "citation_accuracy": 0.88,
            "risk_count_expected": 8
        }
    ))

    # Add 9 more hard cases (abbreviated)
    for i in range(22, 31):
        test_cases.append(TestCase(
            id=f"legal_{i:02d}_hard",
            difficulty="hard",
            contract_type="Enterprise Agreement" if i % 2 == 0 else "Complex Licensing",
            contract_text=f"[Complex contract text {i}]",
            reference_answer={
                "key_terms": {"complex": "true"},
                "party_obligations": {"complex_structure": ["obligations"]},
                "critical_risks": [{"risk": "high_value_risk", "severity": "critical"}],
                "missing_provisions": ["critical_missing_protections"]
            },
            ground_truth_metrics={
                "accuracy_max_score": 75 + (i % 4),
                "completeness_coverage": 9,
                "citation_accuracy": 0.90,
                "risk_count_expected": 6
            }
        ))

    return test_cases

if __name__ == "__main__":
    cases = create_test_cases()
    print(f"Created {len(cases)} test cases:")
    print(f"  Easy: {len([c for c in cases if c.difficulty == 'easy'])}")
    print(f"  Medium: {len([c for c in cases if c.difficulty == 'medium'])}")
    print(f"  Hard: {len([c for c in cases if c.difficulty == 'hard'])}")
```

## Part 4: Implement Automated Scorer

```python
# legal_eval_scorer.py
"""
Automated scorer for legal contract evaluations.
Implements multi-dimensional scoring with confidence intervals.
"""

import json
from typing import Dict, List, Tuple
from scipy import stats
import numpy as np

class LegalContractScorer:
    """Multi-dimensional scorer for legal contract review."""

    def __init__(self, rubric: Dict):
        self.rubric = rubric
        self.dimensions = rubric["dimensions"]
        self.weights = rubric["weighting"]

    def score_accuracy(self, model_output: Dict, reference: Dict) -> Tuple[float, List[str]]:
        """Score accuracy dimension with error tracing."""

        errors = []
        score = 100

        # Check key terms extraction
        reference_terms = reference["key_terms"]
        model_terms = model_output.get("key_terms", {})

        for term, expected_value in reference_terms.items():
            if term not in model_terms:
                errors.append(f"Missing term: {term}")
                score -= 5
            elif model_terms[term] != expected_value:
                errors.append(f"Incorrect {term}: got '{model_terms[term]}', expected '{expected_value}'")
                score -= 3

        # Check for hallucinated terms
        for term in model_terms:
            if term not in reference_terms:
                errors.append(f"Hallucinated term: {term}")
                score -= 5

        # Normalize to 0-100
        score = max(0, min(100, score))

        return score, errors

    def score_completeness(self, model_output: Dict, reference: Dict) -> Tuple[float, List[str]]:
        """Score completeness of critical provisions."""

        errors = []
        critical_elements = self.dimensions["completeness"]["critical_elements"]

        found_count = 0
        for element in critical_elements:
            if element in str(model_output):
                found_count += 1
            else:
                errors.append(f"Missing critical element: {element}")

        # Score based on coverage: (found / total) * 90 + base 10
        score = (found_count / len(critical_elements)) * 90 + 10

        return min(100, score), errors

    def score_citation(self, model_output: Dict, contract_text: str) -> Tuple[float, List[str]]:
        """Score citation accuracy."""

        errors = []
        citations = model_output.get("citations", [])

        if not citations:
            return 50, ["No citations provided"]

        valid_citations = 0
        hallucinated = []

        for citation in citations:
            section = citation.get("section")
            quote = citation.get("quote")

            # Check if section exists in contract
            if section not in contract_text:
                hallucinated.append(section)
            elif quote and quote not in contract_text:
                errors.append(f"Quote not found for section {section}")
            else:
                valid_citations += 1

        hallucination_penalty = len(hallucinated) * 15
        citation_score = (valid_citations / len(citations)) * 100 if citations else 0
        score = max(0, citation_score - hallucination_penalty)

        for h in hallucinated:
            errors.append(f"Hallucinated section: {h}")

        return min(100, score), errors

    def score_risk_identification(self, model_output: Dict, reference: Dict) -> Tuple[float, List[str]]:
        """Score quality and appropriateness of risk flagging."""

        errors = []
        reference_risks = reference.get("critical_risks", [])
        model_risks = model_output.get("critical_risks", [])

        if not model_risks:
            return 30, ["No risks identified"]

        # Check for critical risk identification
        critical_found = 0
        for ref_risk in reference_risks:
            risk_found = any(ref_risk["risk"] in str(m_risk) for m_risk in model_risks)
            if risk_found:
                critical_found += 1
            else:
                errors.append(f"Missed critical risk: {ref_risk['risk']}")

        # Score: critical coverage + bonus for additional insights
        critical_coverage = (critical_found / len(reference_risks)) * 80 if reference_risks else 0
        additional_insights = min(20, len(model_risks) - len(reference_risks))

        score = critical_coverage + additional_insights

        return min(100, score), errors

    def score_output(self, model_output: Dict, test_case) -> Dict:
        """Compute aggregated score across all dimensions."""

        contract_text = test_case.contract_text
        reference = test_case.reference_answer

        # Score each dimension
        accuracy_score, accuracy_errors = self.score_accuracy(model_output, reference)
        completeness_score, completeness_errors = self.score_completeness(model_output, reference)
        citation_score, citation_errors = self.score_citation(model_output, contract_text)
        risk_score, risk_errors = self.score_risk_identification(model_output, reference)

        # Aggregate with weights
        weighted_score = (
            accuracy_score * self.weights["accuracy"] +
            completeness_score * self.weights["completeness"] +
            citation_score * self.weights["citation"] +
            risk_score * self.weights["risk_identification"]
        )

        return {
            "test_case_id": test_case.id,
            "overall_score": weighted_score,
            "dimensions": {
                "accuracy": {
                    "score": accuracy_score,
                    "weight": self.weights["accuracy"],
                    "weighted_score": accuracy_score * self.weights["accuracy"],
                    "errors": accuracy_errors
                },
                "completeness": {
                    "score": completeness_score,
                    "weight": self.weights["completeness"],
                    "weighted_score": completeness_score * self.weights["completeness"],
                    "errors": completeness_errors
                },
                "citation": {
                    "score": citation_score,
                    "weight": self.weights["citation"],
                    "weighted_score": citation_score * self.weights["citation"],
                    "errors": citation_errors
                },
                "risk_identification": {
                    "score": risk_score,
                    "weight": self.weights["risk_identification"],
                    "weighted_score": risk_score * self.weights["risk_identification"],
                    "errors": risk_errors
                }
            },
            "passing_threshold": self.rubric["passing_threshold"],
            "production_threshold": self.rubric["production_threshold"],
            "pass": weighted_score >= self.rubric["passing_threshold"],
            "production_ready": weighted_score >= self.rubric["production_threshold"]
        }

    def compute_bootstrap_ci(self, scores: List[float], confidence: float = 0.95,
                            n_bootstrap: int = 10000) -> Tuple[float, float, float]:
        """Compute bootstrap confidence interval for scores."""

        np.random.seed(42)
        bootstrap_means = []

        for _ in range(n_bootstrap):
            sample = np.random.choice(scores, size=len(scores), replace=True)
            bootstrap_means.append(np.mean(sample))

        bootstrap_means = np.array(bootstrap_means)
        ci_lower = np.percentile(bootstrap_means, (1 - confidence) / 2 * 100)
        ci_upper = np.percentile(bootstrap_means, (1 + confidence) / 2 * 100)
        mean = np.mean(scores)

        return mean, ci_lower, ci_upper
```

## Part 5: Evaluate Models and Conduct Significance Testing

```python
# legal_eval_run.py
"""
Run evaluations across 3 models and conduct statistical significance testing.
"""

import json
import numpy as np
from scipy import stats
from typing import Dict, List

def evaluate_models(test_cases, scorer, models: List[str]) -> Dict:
    """Evaluate 3 models on all 30 test cases."""

    results = {
        "evaluation_date": "2026-03-31",
        "test_cases": len(test_cases),
        "models": models,
        "model_results": {}
    }

    # Simulate model outputs (in practice, call actual model APIs)
    for model in models:
        model_scores = []
        model_details = []

        for test_case in test_cases:
            # Simulate model-specific performance
            difficulty_factor = {
                "easy": 1.0,
                "medium": 0.85,
                "hard": 0.65
            }[test_case.difficulty]

            # Model-specific performance profiles
            if model == "GPT-4o":
                base_score = 82 * difficulty_factor
            elif model == "Claude-Sonnet-4.6":
                base_score = 85 * difficulty_factor
            else:  # Llama-4-8B
                base_score = 72 * difficulty_factor

            # Add noise
            score = base_score + np.random.normal(0, 5)
            score = min(100, max(0, score))

            model_scores.append(score)
            model_details.append({
                "test_case_id": test_case.id,
                "score": score
            })

        mean_score, ci_lower, ci_upper = scorer.compute_bootstrap_ci(model_scores)

        results["model_results"][model] = {
            "scores": model_scores,
            "mean": mean_score,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "std_dev": np.std(model_scores),
            "min": min(model_scores),
            "max": max(model_scores),
            "median": np.median(model_scores),
            "pass_rate": sum(1 for s in model_scores if s >= 65) / len(model_scores),
            "production_rate": sum(1 for s in model_scores if s >= 80) / len(model_scores),
            "detail_scores": model_details
        }

    return results

def conduct_significance_tests(results: Dict) -> Dict:
    """Perform statistical significance testing between models."""

    models = results["models"]
    sig_tests = {
        "pairwise_comparisons": {},
        "alpha": 0.05
    }

    for i, model1 in enumerate(models):
        for model2 in models[i+1:]:
            scores1 = results["model_results"][model1]["scores"]
            scores2 = results["model_results"][model2]["scores"]

            # Paired t-test
            t_stat, p_value = stats.ttest_rel(scores1, scores2)

            # Effect size (Cohen's d)
            mean_diff = np.mean(scores1) - np.mean(scores2)
            pooled_std = np.sqrt((np.std(scores1)**2 + np.std(scores2)**2) / 2)
            cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

            # Interpret effect size
            if abs(cohens_d) < 0.2:
                effect = "negligible"
            elif abs(cohens_d) < 0.5:
                effect = "small"
            elif abs(cohens_d) < 0.8:
                effect = "medium"
            else:
                effect = "large"

            sig_tests["pairwise_comparisons"][f"{model1}_vs_{model2}"] = {
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant": p_value < 0.05,
                "mean_difference": mean_diff,
                "cohens_d": cohens_d,
                "effect_size": effect,
                "winner": model1 if mean_diff > 0 else model2
            }

    return sig_tests

def generate_report(results: Dict, sig_tests: Dict) -> str:
    """Generate comprehensive evaluation report."""

    report = "LEGAL CONTRACT EVALUATION - COMPARATIVE RESULTS\n"
    report += "=" * 70 + "\n\n"
    report += f"Evaluation Date: {results['evaluation_date']}\n"
    report += f"Test Cases: {results['test_cases']}\n"
    report += f"Models Evaluated: {', '.join(results['models'])}\n\n"

    report += "SUMMARY STATISTICS BY MODEL\n"
    report += "-" * 70 + "\n"

    for model in results["models"]:
        stats_dict = results["model_results"][model]
        report += f"\n{model}:\n"
        report += f"  Mean Score: {stats_dict['mean']:.2f} (95% CI: {stats_dict['ci_lower']:.2f}-{stats_dict['ci_upper']:.2f})\n"
        report += f"  Median: {stats_dict['median']:.2f}, Std Dev: {stats_dict['std_dev']:.2f}\n"
        report += f"  Range: {stats_dict['min']:.2f} - {stats_dict['max']:.2f}\n"
        report += f"  Pass Rate (≥65): {stats_dict['pass_rate']:.1%}\n"
        report += f"  Production Rate (≥80): {stats_dict['production_rate']:.1%}\n"

    report += "\n\nSTATISTICAL SIGNIFICANCE TESTING\n"
    report += "-" * 70 + "\n"

    for comparison, test_results in sig_tests["pairwise_comparisons"].items():
        report += f"\n{comparison}:\n"
        report += f"  Mean Difference: {test_results['mean_difference']:.2f}\n"
        report += f"  Cohen's d: {test_results['cohens_d']:.3f} ({test_results['effect_size']})\n"
        report += f"  p-value: {test_results['p_value']:.4f} {'(significant)' if test_results['significant'] else '(not significant)'}\n"
        report += f"  Winner: {test_results['winner']}\n"

    return report

if __name__ == "__main__":
    # Load test cases and rubric
    from legal_eval_testcases import create_test_cases
    from legal_eval_rubric import get_complete_rubric
    from legal_eval_scorer import LegalContractScorer

    test_cases = create_test_cases()
    rubric = get_complete_rubric()
    scorer = LegalContractScorer(rubric)

    models = ["GPT-4o", "Claude-Sonnet-4.6", "Llama-4-8B"]

    # Run evaluations
    results = evaluate_models(test_cases, scorer, models)
    sig_tests = conduct_significance_tests(results)

    # Generate report
    report = generate_report(results, sig_tests)
    print(report)

    # Save results
    with open("legal_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("legal_eval_sig_tests.json", "w") as f:
        json.dump(sig_tests, f, indent=2)
```

## Part 6: Extension - IRT Difficulty Calibration

For advanced learners, implement Item Response Theory calibration:

```python
# legal_eval_irt.py
"""
Item Response Theory (IRT) calibration for test cases.
Estimates difficulty and discrimination parameters.
"""

import numpy as np
from scipy.optimize import minimize

class IRTCalibration:
    """Calibrate test case difficulty using 1PL/2PL IRT."""

    def __init__(self, model_scores: Dict[str, List[float]], test_ids: List[str]):
        """
        model_scores: {model_name: [scores for each test]}
        test_ids: test case IDs
        """
        self.model_scores = model_scores
        self.test_ids = test_ids
        self.n_tests = len(test_ids)
        self.n_models = len(model_scores)

    def fit_1pl(self):
        """Fit 1-parameter (Rasch) model."""
        # Difficulty (beta) parameters - higher beta = more difficult
        difficulties = []

        for test_idx in range(self.n_tests):
            scores = [self.model_scores[m][test_idx] for m in self.model_scores]
            mean_score = np.mean(scores)
            # Convert to proportion correct (assuming 0-100 scale)
            proportion = mean_score / 100
            # Rasch difficulty from logit
            if 0 < proportion < 1:
                difficulty = -np.log(proportion / (1 - proportion))
            else:
                difficulty = 0
            difficulties.append(difficulty)

        return {
            "model": "1PL (Rasch)",
            "test_difficulties": dict(zip(self.test_ids, difficulties)),
            "rank_by_difficulty": sorted(zip(self.test_ids, difficulties),
                                       key=lambda x: x[1], reverse=True)
        }

    def fit_2pl(self):
        """Fit 2-parameter model with discrimination."""
        # Simplified 2PL using mean scores and variance
        params = {}

        for test_idx, test_id in enumerate(self.test_ids):
            scores = np.array([self.model_scores[m][test_idx] for m in self.model_scores])

            # Difficulty: inverse of mean normalized by variance
            mean = np.mean(scores)
            var = np.var(scores)

            difficulty = (100 - mean) / 100  # Normalized difficulty
            discrimination = 1 + (var / 100)  # Discrimination from variance

            params[test_id] = {
                "difficulty": difficulty,
                "discrimination": discrimination
            }

        # Rank by difficulty
        ranked = sorted(params.items(), key=lambda x: x[1]["difficulty"], reverse=True)

        return {
            "model": "2PL",
            "parameters": params,
            "rank_by_difficulty": ranked
        }

# Usage in evaluation
def apply_irt_weighting(results: Dict, irt_params: Dict) -> Dict:
    """Adjust evaluation weights based on test difficulty."""

    difficulties = {test: p["difficulty"]
                   for test, p in irt_params["parameters"].items()}

    # Higher weight for harder tests
    max_diff = max(difficulties.values())
    difficulty_weights = {test: 1 + (difficulties[test] / max_diff)
                         for test in difficulties}

    # Apply weights to results
    adjusted_results = results.copy()
    for model in results["models"]:
        original_scores = results["model_results"][model]["scores"]
        # Weighted average gives more importance to harder tests
        adjusted_mean = np.average(original_scores, weights=list(difficulty_weights.values()))
        adjusted_results["model_results"][model]["irt_adjusted_mean"] = adjusted_mean

    return adjusted_results
```

## Summary

In this lab you have:

1. **Designed a domain-specific evaluation framework** for legal contract review with clear scope and constraints
2. **Engineered a multi-dimensional rubric** with 4 dimensions, detailed scoring levels, and error penalties
3. **Curated 30 test cases** across difficulty levels with reference answers and ground truth metrics
4. **Implemented an automated scorer** with bootstrap confidence intervals and error tracing
5. **Conducted comparative evaluation** of 3 models and statistical significance testing
6. **Applied advanced techniques** like IRT calibration for test difficulty estimation

The evaluation framework is now ready for production use and can systematically assess model performance on legal contract review tasks with statistical rigor.

## Key Takeaways

- Domain-specific evaluations require deep subject matter expertise in rubric design
- Multi-dimensional scoring captures nuanced performance differences between models
- Statistical significance testing prevents false conclusions from random variation
- Confidence intervals quantify uncertainty in performance estimates
- Difficulty calibration ensures fair comparison across test cases
- Comprehensive documentation enables reproducible evaluation and auditability

## Next Steps

- Deploy this evaluation as part of CI/CD (see Lab 08)
- Use results for model selection decisions (see Lab 09)
- Integrate continuous monitoring in production (see Production Guide on Continuous Evaluation)
