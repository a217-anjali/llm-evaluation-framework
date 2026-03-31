# Lab 02: Building a Rubric-Based LLM Judge

**Difficulty:** Yellow (Intermediate)
**Time Estimate:** 60 minutes
**Tools:** LiteLLM, Claude/GPT-4, Python

## Objectives

By the end of this lab, you will:
- Design a detailed evaluation rubric for summarization quality
- Implement a pointwise LLM judge using LiteLLM
- Collect human labels for 20 test cases
- Measure inter-rater agreement using Cohen's kappa
- Calibrate and iterate on the rubric for better alignment
- Compute agreement statistics between LLM judge and human labels

## Prerequisites

- Python 3.11 or higher
- API access to at least one LLM (OpenAI, Claude, Cohere, etc.)
- API key configured (exported as environment variable)
- Basic understanding of summarization quality
- ~30 minutes to prepare human annotations
- Internet connectivity for API calls

## Setup

### 2.1 Install Dependencies

```bash
mkdir -p ~/llm-judge-lab && cd ~/llm-judge-lab
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install --upgrade pip
pip install litellm==1.33.0
pip install python-dotenv==1.0.0
pip install pandas==2.1.4
pip install scikit-learn==1.4.0
pip install numpy==1.24.3
pip install tqdm==4.66.2
```

### 2.2 Configure API Credentials

Create a `.env` file:
```bash
cat > .env << 'EOF'
# Choose one provider. Examples:

# OpenAI
OPENAI_API_KEY=sk-xxxxx

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Cohere
COHERE_API_KEY=xxxxx

# You can also use environment variables in code
EOF

chmod 600 .env
```

Test API access:
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
print('✓ API key found' if api_key else '✗ No API key configured')
"
```

## Step-by-Step Instructions

### Step 1: Define Evaluation Rubric (8 minutes)

The rubric defines what makes a "good" summary. LLM judges will use this to score submissions.

**File: `rubric.py`**
```python
#!/usr/bin/env python3
"""
Evaluation rubric for summarization quality
"""

SUMMARIZATION_RUBRIC = {
    "completeness": {
        "description": "Does the summary capture all major points from the source text?",
        "score_range": (1, 5),
        "criteria": {
            5: "Captures all major points and key details comprehensively",
            4: "Captures most major points with minor omissions",
            3: "Captures 50-70% of major points; some important details missing",
            2: "Captures fewer than 50% of major points; many critical points missing",
            1: "Misses almost all major points; extremely incomplete"
        }
    },
    "accuracy": {
        "description": "Is the summary factually accurate and free of distortions?",
        "score_range": (1, 5),
        "criteria": {
            5: "Completely accurate; no factual errors or distortions",
            4: "Mostly accurate; 1-2 minor factual nuances missing",
            3: "Some factual inaccuracies or unclear statements (1-2 errors)",
            2: "Multiple factual errors or significant distortions (3+ errors)",
            1: "Severely inaccurate or misleading; mostly incorrect"
        }
    },
    "conciseness": {
        "description": "Is the summary appropriately brief without unnecessary verbosity?",
        "score_range": (1, 5),
        "criteria": {
            5: "Highly concise; no unnecessary words or repetition",
            4: "Concise with minimal redundancy",
            3: "Adequate length but some unnecessary phrases",
            2: "Notably verbose with considerable redundancy",
            1: "Extremely verbose; reads more like an excerpt than a summary"
        }
    },
    "coherence": {
        "description": "Does the summary flow logically and read naturally?",
        "score_range": (1, 5),
        "criteria": {
            5: "Excellent flow; logical transitions; natural, polished writing",
            4: "Good flow with clear structure; mostly natural",
            3: "Adequate coherence; some awkward transitions",
            2: "Poor flow; disjointed or confusing structure",
            1: "Incoherent; very difficult to follow"
        }
    },
    "relevance": {
        "description": "Does the summary focus on the most important information?",
        "score_range": (1, 5),
        "criteria": {
            5: "Perfectly prioritizes essential information",
            4: "Prioritizes most essential information well",
            3: "Includes both essential and some non-essential information",
            2: "Includes significant non-essential information",
            1: "Focuses on minor details; misses essential points"
        }
    }
}

class RubricScorer:
    """Helper for working with the rubric"""

    @staticmethod
    def get_dimensions():
        """Get all evaluation dimensions"""
        return list(SUMMARIZATION_RUBRIC.keys())

    @staticmethod
    def get_criteria(dimension):
        """Get scoring criteria for a dimension"""
        return SUMMARIZATION_RUBRIC[dimension]["criteria"]

    @staticmethod
    def get_prompt_section(dimension):
        """Get rubric text for prompting"""
        rubric = SUMMARIZATION_RUBRIC[dimension]
        prompt = f"**{dimension.upper()}** (1-5 scale):\n"
        prompt += f"{rubric['description']}\n\n"

        for score in sorted(rubric['criteria'].keys(), reverse=True):
            prompt += f"- {score}: {rubric['criteria'][score]}\n"

        return prompt

    @staticmethod
    def get_full_rubric_text():
        """Get the complete rubric for evaluation prompts"""
        text = "EVALUATION RUBRIC\n"
        text += "=" * 60 + "\n\n"

        for dimension in SUMMARIZATION_RUBRIC.keys():
            text += RubricScorer.get_prompt_section(dimension) + "\n"

        return text

if __name__ == "__main__":
    print(RubricScorer.get_full_rubric_text())
```

Run it to verify:
```bash
python rubric.py
```

### Step 2: Create Test Dataset (12 minutes)

Create 20 test cases with document, reference summary, and candidate summaries.

**File: `dataset.py`**
```python
#!/usr/bin/env python3
"""
Test dataset for summarization evaluation
"""

import json
from pathlib import Path

# 20 document-summary pairs for evaluation
TEST_DATASET = [
    {
        "id": "doc_001",
        "source": """
            The Amazon rainforest, often referred to as the "lungs of the Earth," spans
            across nine countries, with Brazil accounting for approximately 60% of the forest.
            This vast ecosystem contains over 390 billion individual trees representing about
            16,000 species. The forest plays a critical role in regulating Earth's climate
            by absorbing massive amounts of carbon dioxide. Additionally, it is home to
            approximately 10% of all species on Earth, including jaguars, anacondas, and
            poison dart frogs. Indigenous peoples have inhabited the rainforest for thousands
            of years, developing intricate knowledge systems and sustainable practices.
            However, deforestation has destroyed approximately 17% of the forest's original extent,
            primarily due to cattle ranching, agriculture, and logging. Scientists warn that
            losing 20-25% of the forest could trigger a tipping point, transforming it into
            a savanna and releasing billions of tons of stored carbon into the atmosphere.
        """,
        "reference_summary": """
            The Amazon rainforest spans nine countries and contains 390 billion trees
            representing 16,000 species. It regulates Earth's climate and houses 10% of
            all species. Indigenous peoples have lived sustainably there for millennia.
            However, 17% has been lost to deforestation. Scientists warn that losing 20-25%
            could trigger irreversible transformation and massive carbon release.
        """,
        "candidate_summaries": {
            "good": """
                The Amazon rainforest, spanning nine countries with Brazil containing 60%,
                comprises 390 billion trees of 16,000 species. It regulates global climate by
                absorbing CO2 and hosts 10% of Earth's species. Indigenous peoples have
                maintained sustainable practices there for millennia. Despite this, 17% has
                been lost to deforestation, and reaching 20-25% loss could irreversibly
                transform it into savanna, releasing massive carbon stores.
            """,
            "poor": """
                The rainforest is in the Amazon and has trees. It's very big and has
                many animals. People live there too. Some parts are being cut down which
                is not good. The forest is important for the planet.
            """,
            "medium": """
                The Amazon rainforest is a huge forest spanning nine countries with many
                species living there. It helps regulate the climate. It has been damaged by
                deforestation for cattle and agriculture. Indigenous people live in the forest.
            """
        }
    },
    {
        "id": "doc_002",
        "source": """
            Photosynthesis is the biological process by which plants, algae, and certain
            bacteria convert light energy from the sun into chemical energy stored in glucose.
            This process occurs primarily in the chloroplasts of plant cells, where the
            pigment chlorophyll absorbs photons. The process can be divided into two main stages:
            the light-dependent reactions and the light-independent reactions (Calvin cycle).
            During light-dependent reactions, water is split, releasing oxygen as a byproduct
            and generating ATP and NADPH. The Calvin cycle then uses these products to convert
            carbon dioxide into glucose through a series of enzymatic reactions. The overall
            equation is 6CO2 + 6H2O + light energy → C6H12O6 + 6O2.
            Photosynthesis is fundamental to nearly all life on Earth, as it produces oxygen
            for respiration and forms the base of most food chains. Global photosynthesis
            annually fixes approximately 100-150 billion tons of carbon, making it the most
            important chemical process on the planet.
        """,
        "reference_summary": """
            Photosynthesis converts light energy into glucose in plant chloroplasts.
            It comprises two stages: light-dependent reactions (splitting water to produce
            oxygen, ATP, and NADPH) and the Calvin cycle (converting CO2 to glucose).
            This process is essential for life, producing oxygen and forming food chain bases,
            and globally fixes 100-150 billion tons of carbon annually.
        """,
        "candidate_summaries": {
            "good": """
                Photosynthesis is a process where plants convert sunlight into chemical energy
                (glucose) in chloroplasts through two stages: light-dependent reactions that
                split water and produce oxygen and energy carriers (ATP, NADPH), and the Calvin
                cycle that converts CO2 to glucose. This process is vital for life, producing
                oxygen and supporting food chains globally.
            """,
            "poor": """
                Plants make food from sunlight. It happens in the green parts of plants.
                Oxygen is made. The sun's energy is used. It's very important.
            """,
            "medium": """
                Photosynthesis is how plants turn sunlight into energy. It happens in two stages
                with reactions involving light and carbon dioxide. Oxygen is produced as a result.
                It's important for life on Earth.
            """
        }
    },
    {
        "id": "doc_003",
        "source": """
            Machine learning has revolutionized how computers process information and make
            decisions. Unlike traditional programming, where rules are explicitly coded,
            machine learning systems learn patterns from data. Supervised learning involves
            training on labeled data; the model learns to map inputs to outputs. Unsupervised
            learning finds hidden patterns without labels. Reinforcement learning trains models
            through reward signals. Recent breakthroughs in deep learning—neural networks with
            many layers—have enabled remarkable achievements in image recognition, natural
            language processing, and game playing. Transformer models, introduced in 2017,
            revolutionized NLP by enabling parallel processing of text. Large language models
            like GPT-4 and Claude, trained on billions of tokens, demonstrate emergent abilities
            in reasoning, coding, and creative tasks. However, challenges remain: models can
            hallucinate false information, require enormous computational resources, and raise
            questions about bias, fairness, and environmental impact.
        """,
        "reference_summary": """
            Machine learning enables computers to learn patterns from data rather than
            relying on explicit rules. Key paradigms include supervised, unsupervised, and
            reinforcement learning. Deep learning and transformers have driven breakthroughs
            in vision and NLP. Modern large language models show emergent reasoning and coding
            abilities but face challenges including hallucinations, high computational costs,
            and concerns about bias and environmental impact.
        """,
        "candidate_summaries": {
            "good": """
                Machine learning allows computers to learn patterns from data through supervised,
                unsupervised, and reinforcement learning approaches. Deep neural networks and
                transformer models have enabled major advances in image recognition and natural
                language processing. Large language models demonstrate impressive reasoning and
                creative abilities, though challenges persist with hallucinations, computational
                demands, bias concerns, and environmental costs.
            """,
            "poor": """
                Machine learning is when computers learn. Deep learning is computers learning
                with many layers. Models can be used for many things like pictures and language.
                There are some problems with them.
            """,
            "medium": """
                Machine learning helps computers learn from data. Supervised learning uses labeled
                data, unsupervised finds patterns, and reinforcement learning uses rewards.
                Deep learning and transformers are important. Large language models are powerful
                but have some issues.
            """
        }
    },
    {
        "id": "doc_004",
        "source": """
            Climate change is altering precipitation patterns across the globe, with significant
            implications for water availability. Warmer temperatures increase atmospheric moisture
            holding capacity (approximately 7% per degree Celsius), leading to more intense rainfall
            in some regions while creating persistent droughts in others. The Arctic, warming twice
            as fast as the global average, is experiencing unprecedented changes. Sea ice loss
            disrupts ocean circulation patterns, particularly the Atlantic Meridional Overturning
            Circulation, which delivers warm water to the North Atlantic. Mountain snowpack,
            critical for water supply in regions like California and the Himalayas, is declining
            due to earlier melting and reduced snow accumulation. Glaciers are retreating worldwide,
            with implications for sea level rise and downstream water resources. Small island nations
            and coastal cities face existential threats from rising sea levels and increased storm
            surge intensity. These changes are interconnected; altered precipitation affects
            agriculture, hydropower generation, and freshwater availability for billions.
        """,
        "reference_summary": """
            Climate change intensifies precipitation extremes: warmer temperatures increase
            atmospheric moisture by ~7% per °C, causing intense rainfall in some regions and
            droughts in others. Arctic warming (2x global rate) disrupts ocean circulation.
            Mountain snowpack and glaciers are declining, threatening water supplies and
            raising sea levels. These interconnected changes threaten agriculture, energy,
            and freshwater access globally.
        """,
        "candidate_summaries": {
            "good": """
                Climate change intensifies precipitation extremes: warmer air holds 7% more
                moisture per degree Celsius, causing intense rainfall in some regions while
                creating droughts elsewhere. Arctic warming (2x global rate) disrupts ocean
                circulation. Declining mountain snowpack and glaciers threaten water supplies
                and accelerate sea level rise, impacting agriculture, hydropower, and
                freshwater availability worldwide.
            """,
            "poor": """
                Climate change is making weather different. It's getting warmer and the
                weather patterns are changing. This affects water and ice. It's a problem
                for many places.
            """,
            "medium": """
                Warmer temperatures are changing where and how much rain falls. The Arctic
                is warming very quickly. Snowpack and glaciers are melting. Sea levels are
                rising. This affects water availability and agriculture.
            """
        }
    },
    {
        "id": "doc_005",
        "source": """
            The human immune system is a complex network of organs, cells, and molecules that
            work together to defend against pathogens. The innate immune system provides the
            first line of defense through physical barriers like skin and chemical barriers
            like stomach acid, as well as specialized cells including macrophages and natural
            killer cells. The adaptive immune system, which develops over time, includes B cells
            that produce antibodies and T cells that directly destroy infected cells. These
            components communicate through signaling molecules called cytokines. Vaccines work
            by training the adaptive immune system to recognize specific pathogens without
            causing disease. Memory cells created during vaccination enable rapid response to
            future infections. However, immune tolerance—the body's ability to avoid attacking
            itself—sometimes fails, leading to autoimmune diseases like rheumatoid arthritis and
            lupus. Immunosenescence, the decline of immune function with age, makes older adults
            more vulnerable to infections.
        """,
        "reference_summary": """
            The immune system has two components: innate (physical and chemical barriers,
            macrophages, natural killer cells) and adaptive (antibodies from B cells,
            T cell-mediated responses). These communicate via cytokines. Vaccines train the
            adaptive immune system, creating memory cells for rapid future response. Immune
            tolerance failures cause autoimmune diseases, while immunosenescence reduces
            immune function in older adults.
        """,
        "candidate_summaries": {
            "good": """
                The immune system comprises innate and adaptive components. Innate immunity
                includes physical barriers, chemical defenses, and specialized cells like
                macrophages. Adaptive immunity involves B cells producing antibodies and
                T cells destroying infected cells. Vaccines train adaptive immunity to recognize
                pathogens, creating memory cells for rapid future response. When immune
                tolerance fails, autoimmune diseases develop; aging reduces immune function.
            """,
            "poor": """
                The body has a system that fights infections. It has different parts that
                work together. Some parts are there from birth, others develop. Vaccines help
                the immune system learn.
            """,
            "medium": """
                The immune system has two types: innate and adaptive. Innate includes skin
                and chemical barriers. Adaptive includes cells that make antibodies. Vaccines
                train immunity. Sometimes the immune system attacks the body itself causing
                autoimmune diseases.
            """
        }
    }
]

def load_dataset():
    """Load the test dataset"""
    return TEST_DATASET

def save_dataset(filepath="test_dataset.json"):
    """Save dataset to JSON"""
    with open(filepath, 'w') as f:
        json.dump(TEST_DATASET, f, indent=2)
    print(f"✓ Dataset saved to {filepath}")

def get_test_cases():
    """Get formatted test cases for evaluation"""
    test_cases = []
    for doc in TEST_DATASET:
        for summary_type in ["good", "medium", "poor"]:
            test_cases.append({
                "doc_id": doc["id"],
                "source": doc["source"].strip(),
                "reference": doc["reference_summary"].strip(),
                "candidate": doc["candidate_summaries"][summary_type].strip(),
                "expected_quality": summary_type
            })
    return test_cases

if __name__ == "__main__":
    save_dataset()
    test_cases = get_test_cases()
    print(f"Created {len(test_cases)} test cases")
    for tc in test_cases[:2]:
        print(f"  - {tc['doc_id']}/{tc['expected_quality']}")
```

Run it:
```bash
python dataset.py
```

### Step 3: Collect Human Labels (15 minutes)

Create a script for human annotation. In practice, you'd use a labeling interface, but for this lab, we'll use simple CSV input.

**File: `annotate_human.py`**
```python
#!/usr/bin/env python3
"""
Collect human annotations for test cases
"""

import json
import csv
from pathlib import Path
from dataset import get_test_cases
from rubric import RubricScorer

def create_annotation_template():
    """Create CSV template for human annotations"""

    test_cases = get_test_cases()

    # Create header
    header = [
        "case_id",
        "doc_id",
        "source",
        "candidate_summary",
        "completeness_score",
        "accuracy_score",
        "conciseness_score",
        "coherence_score",
        "relevance_score",
        "overall_score",
        "notes"
    ]

    # Write to CSV
    filepath = "annotations_template.csv"
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for i, tc in enumerate(test_cases):
            writer.writerow([
                i + 1,
                tc["doc_id"],
                tc["source"][:100] + "...",  # Truncate for readability
                tc["candidate"][:100] + "...",
                "",  # To be filled by human
                "",
                "",
                "",
                "",
                "",
                ""
            ])

    print(f"✓ Annotation template created: {filepath}")
    print(f"  Open in Excel/Sheets and fill scores (1-5 for each dimension)")
    return filepath

def create_sample_annotations():
    """
    For lab purposes, create pre-filled human annotations
    These represent what a human annotator would provide
    """

    # Simulated human judgments
    # In reality, these would come from actual human annotators
    human_labels = [
        # doc_001 - Amazon rainforest
        {"case_id": 1, "doc_id": "doc_001", "type": "good",
         "scores": {"completeness": 5, "accuracy": 5, "conciseness": 4, "coherence": 5, "relevance": 5}},
        {"case_id": 2, "doc_id": "doc_001", "type": "medium",
         "scores": {"completeness": 3, "accuracy": 4, "conciseness": 4, "coherence": 3, "relevance": 3}},
        {"case_id": 3, "doc_id": "doc_001", "type": "poor",
         "scores": {"completeness": 1, "accuracy": 2, "conciseness": 1, "coherence": 2, "relevance": 1}},

        # doc_002 - Photosynthesis
        {"case_id": 4, "doc_id": "doc_002", "type": "good",
         "scores": {"completeness": 5, "accuracy": 5, "conciseness": 5, "coherence": 5, "relevance": 5}},
        {"case_id": 5, "doc_id": "doc_002", "type": "medium",
         "scores": {"completeness": 3, "accuracy": 3, "conciseness": 3, "coherence": 3, "relevance": 3}},
        {"case_id": 6, "doc_id": "doc_002", "type": "poor",
         "scores": {"completeness": 2, "accuracy": 2, "conciseness": 2, "coherence": 2, "relevance": 2}},

        # doc_003 - Machine Learning
        {"case_id": 7, "doc_id": "doc_003", "type": "good",
         "scores": {"completeness": 5, "accuracy": 5, "conciseness": 4, "coherence": 5, "relevance": 5}},
        {"case_id": 8, "doc_id": "doc_003", "type": "medium",
         "scores": {"completeness": 3, "accuracy": 3, "conciseness": 3, "coherence": 3, "relevance": 3}},
        {"case_id": 9, "doc_id": "doc_003", "type": "poor",
         "scores": {"completeness": 1, "accuracy": 2, "conciseness": 1, "coherence": 1, "relevance": 1}},

        # doc_004 - Climate Change
        {"case_id": 10, "doc_id": "doc_004", "type": "good",
         "scores": {"completeness": 5, "accuracy": 5, "conciseness": 5, "coherence": 5, "relevance": 5}},
        {"case_id": 11, "doc_id": "doc_004", "type": "medium",
         "scores": {"completeness": 3, "accuracy": 3, "conciseness": 4, "coherence": 3, "relevance": 3}},
        {"case_id": 12, "doc_id": "doc_004", "type": "poor",
         "scores": {"completeness": 2, "accuracy": 1, "conciseness": 2, "coherence": 1, "relevance": 2}},

        # doc_005 - Immune System
        {"case_id": 13, "doc_id": "doc_005", "type": "good",
         "scores": {"completeness": 5, "accuracy": 5, "conciseness": 4, "coherence": 5, "relevance": 5}},
        {"case_id": 14, "doc_id": "doc_005", "type": "medium",
         "scores": {"completeness": 3, "accuracy": 4, "conciseness": 3, "coherence": 3, "relevance": 3}},
        {"case_id": 15, "doc_id": "doc_005", "type": "poor",
         "scores": {"completeness": 2, "accuracy": 2, "conciseness": 2, "coherence": 1, "relevance": 1}},
    ]

    filepath = "human_annotations.json"
    with open(filepath, 'w') as f:
        json.dump(human_labels, f, indent=2)

    print(f"✓ Sample human annotations created: {filepath}")
    return filepath, human_labels

if __name__ == "__main__":
    create_annotation_template()
    filepath, labels = create_sample_annotations()
    print(f"\nLoaded {len(labels)} human annotations")
```

Run it:
```bash
python annotate_human.py
```

### Step 4: Implement LLM Judge (20 minutes)

Create a judge that uses an LLM to score summaries according to the rubric.

**File: `llm_judge.py`**
```python
#!/usr/bin/env python3
"""
LLM-based judge for summarization evaluation
"""

import json
from typing import Dict, List
import re
from litellm import completion
from rubric import SUMMARIZATION_RUBRIC, RubricScorer
import os
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    """Judge summaries using an LLM"""

    def __init__(self, model="gpt-4", temperature=0.3):
        """
        Initialize the judge

        Args:
            model: LLM model to use (gpt-4, claude-3-opus, command, etc.)
            temperature: Temperature for generation (lower = more consistent)
        """
        self.model = model
        self.temperature = temperature
        self.rubric_text = RubricScorer.get_full_rubric_text()

    def create_judge_prompt(self, source: str, candidate: str) -> str:
        """
        Create a prompt for the judge to score a summary
        """
        prompt = f"""You are an expert evaluator of text summarization.

{self.rubric_text}

TASK: Evaluate the quality of the following summary based on the rubric above.

SOURCE TEXT:
{source}

SUMMARY TO EVALUATE:
{candidate}

Provide scores for each dimension (1-5) and explain your reasoning briefly.

Format your response EXACTLY as follows:
COMPLETENESS: [score] - [brief explanation]
ACCURACY: [score] - [brief explanation]
CONCISENESS: [score] - [brief explanation]
COHERENCE: [score] - [brief explanation]
RELEVANCE: [score] - [brief explanation]
OVERALL: [score] - [brief overall assessment]
"""
        return prompt

    def judge_summary(self, source: str, candidate: str) -> Dict:
        """
        Judge a single summary

        Args:
            source: Original text
            candidate: Summary to evaluate

        Returns:
            Dictionary with scores and explanations
        """
        prompt = self.create_judge_prompt(source, candidate)

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=500,
                timeout=30
            )

            response_text = response.choices[0].message.content

            # Parse response
            scores = self._parse_response(response_text)
            scores['raw_response'] = response_text

            return scores

        except Exception as e:
            print(f"✗ Error calling LLM: {e}")
            return {
                "completeness": 0,
                "accuracy": 0,
                "conciseness": 0,
                "coherence": 0,
                "relevance": 0,
                "overall": 0,
                "error": str(e)
            }

    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse LLM response to extract scores
        """
        scores = {}
        dimensions = ["completeness", "accuracy", "conciseness", "coherence", "relevance", "overall"]

        for dimension in dimensions:
            # Find pattern like "DIMENSION: [score]"
            pattern = rf'{dimension.upper()}:\s*(\d)'
            match = re.search(pattern, response_text, re.IGNORECASE)

            if match:
                scores[dimension] = int(match.group(1))
            else:
                scores[dimension] = 0  # Default if not found

        return scores

    def judge_batch(self, test_cases: List[Dict], verbose=True) -> List[Dict]:
        """
        Judge multiple summaries

        Args:
            test_cases: List of test cases with 'source' and 'candidate' keys
            verbose: Print progress

        Returns:
            List of results with scores
        """
        results = []

        for i, tc in enumerate(test_cases):
            if verbose:
                print(f"Judging {i+1}/{len(test_cases)}...")

            scores = self.judge_summary(tc['source'], tc['candidate'])
            scores['case_id'] = tc.get('case_id', i)
            scores['doc_id'] = tc.get('doc_id', '')

            results.append(scores)

        return results

if __name__ == "__main__":
    from dataset import get_test_cases

    # Test with a few cases
    judge = LLMJudge(model="gpt-4")
    test_cases = get_test_cases()[:3]  # Just 3 for testing

    print("Testing LLM Judge...")
    results = judge.judge_batch(test_cases)

    print("\n" + "="*60)
    print("Sample Results:")
    for result in results:
        print(f"\nCase {result.get('case_id', '?')}:")
        print(f"  Completeness: {result['completeness']}")
        print(f"  Accuracy: {result['accuracy']}")
        print(f"  Conciseness: {result['conciseness']}")
        print(f"  Coherence: {result['coherence']}")
        print(f"  Relevance: {result['relevance']}")
        print(f"  Overall: {result['overall']}")
```

Test the judge:
```bash
python llm_judge.py
```

### Step 5: Compute Agreement with Human Labels (15 minutes)

**File: `compute_agreement.py`**
```python
#!/usr/bin/env python3
"""
Compute agreement between LLM judge and human labels
"""

import json
import numpy as np
from sklearn.metrics import cohen_kappa_score, mean_absolute_error, pearsonr
from llm_judge import LLMJudge
from dataset import get_test_cases
from annotate_human import create_sample_annotations

def load_human_annotations(filepath="human_annotations.json"):
    """Load human annotations"""
    with open(filepath) as f:
        return json.load(f)

def compute_kappa(human_scores: list, llm_scores: list) -> float:
    """
    Compute Cohen's kappa between human and LLM scores

    Kappa measures agreement between raters:
    - 1.0: Perfect agreement
    - 0.81+: Almost perfect
    - 0.61-0.80: Substantial
    - 0.41-0.60: Moderate
    - 0.21-0.40: Fair
    - 0.0-0.20: Slight
    - <0: Less than chance
    """
    return cohen_kappa_score(human_scores, llm_scores, labels=[1, 2, 3, 4, 5])

def analyze_agreement(human_labels: list, llm_results: list) -> Dict:
    """
    Comprehensive agreement analysis
    """
    dimensions = ["completeness", "accuracy", "conciseness", "coherence", "relevance"]
    results = {}

    print("\n" + "="*70)
    print("AGREEMENT ANALYSIS: Human vs LLM Judge")
    print("="*70)

    for dimension in dimensions:
        human_scores = [label['scores'][dimension] for label in human_labels]
        llm_scores = [result[dimension] for result in llm_results]

        # Cohen's kappa
        kappa = compute_kappa(human_scores, llm_scores)

        # Mean absolute error
        mae = mean_absolute_error(human_scores, llm_scores)

        # Pearson correlation
        correlation, p_value = pearsonr(human_scores, llm_scores)

        results[dimension] = {
            "kappa": kappa,
            "mae": mae,
            "correlation": correlation,
            "p_value": p_value,
            "human_mean": np.mean(human_scores),
            "llm_mean": np.mean(llm_scores),
        }

        # Print results
        print(f"\n{dimension.upper()}")
        print(f"  Cohen's Kappa: {kappa:.3f}", end="")

        if kappa >= 0.81:
            print(" [Almost Perfect]")
        elif kappa >= 0.61:
            print(" [Substantial]")
        elif kappa >= 0.41:
            print(" [Moderate]")
        else:
            print(" [Fair/Slight]")

        print(f"  Mean Absolute Error: {mae:.2f}")
        print(f"  Correlation: {correlation:.3f} (p={p_value:.4f})")
        print(f"  Human mean: {np.mean(human_scores):.2f}")
        print(f"  LLM mean: {np.mean(llm_scores):.2f}")

    # Overall agreement
    all_human = [s for label in human_labels for s in label['scores'].values()]
    all_llm = [s for result in llm_results for d in dimensions if d in result for s in [result[d]]]

    overall_kappa = compute_kappa(all_human[:len(all_llm)], all_llm)

    print(f"\n{'='*70}")
    print(f"OVERALL AGREEMENT: {overall_kappa:.3f}")
    print(f"{'='*70}")

    return results

def calibration_analysis(human_labels: list, llm_results: list):
    """
    Analyze calibration: is the judge biased high/low?
    """
    print("\n" + "="*70)
    print("CALIBRATION ANALYSIS")
    print("="*70)

    dimensions = ["completeness", "accuracy", "conciseness", "coherence", "relevance"]

    for dimension in dimensions:
        human_scores = [label['scores'][dimension] for label in human_labels]
        llm_scores = [result[dimension] for result in llm_results]

        human_mean = np.mean(human_scores)
        llm_mean = np.mean(llm_scores)
        bias = llm_mean - human_mean

        print(f"\n{dimension.upper()}")
        print(f"  Human average: {human_mean:.2f}")
        print(f"  LLM average: {llm_mean:.2f}")
        print(f"  Bias (LLM - Human): {bias:+.2f}", end="")

        if abs(bias) < 0.2:
            print(" [Well-calibrated]")
        elif bias > 0.5:
            print(" [LLM too generous]")
        elif bias < -0.5:
            print(" [LLM too harsh]")
        else:
            print(" [Slightly biased]")

if __name__ == "__main__":
    from typing import Dict

    # Load human annotations
    filepath, human_labels = create_sample_annotations()

    # Get test cases
    test_cases = get_test_cases()

    # Judge with LLM
    print("Running LLM judge on test cases...")
    judge = LLMJudge(model="gpt-4")
    llm_results = judge.judge_batch(test_cases, verbose=True)

    # Save results
    with open("llm_judge_results.json", "w") as f:
        json.dump(llm_results, f, indent=2)
    print("✓ Results saved to llm_judge_results.json")

    # Compute agreement
    agreement = analyze_agreement(human_labels, llm_results)

    # Calibration analysis
    calibration_analysis(human_labels, llm_results)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
If Cohen's kappa > 0.60:
  ✓ Good agreement! Judge is reliable.

If Cohen's kappa 0.40-0.60:
  ~ Moderate agreement. Consider rubric refinement.

If Cohen's kappa < 0.40:
  ✗ Poor agreement. Rubric needs revision.

If bias exists:
  - Revise rubric criteria
  - Adjust prompt instructions
  - Recalibrate on examples
""")
```

### Step 6: Iterate and Refine (10 minutes)

Based on agreement metrics, refine the rubric.

**File: `refine_rubric.py`**
```python
#!/usr/bin/env python3
"""
Refine rubric based on agreement analysis
"""

import json

def suggest_rubric_improvements(agreement_results: dict):
    """
    Suggest improvements based on agreement analysis
    """
    print("\n" + "="*70)
    print("RUBRIC REFINEMENT SUGGESTIONS")
    print("="*70)

    for dimension, metrics in agreement_results.items():
        kappa = metrics['kappa']

        if kappa < 0.40:
            print(f"\n{dimension.upper()} - NEEDS REVISION")
            print(f"  Current kappa: {kappa:.3f}")
            print("  Suggestions:")
            print("  1. Criteria boundaries are ambiguous")
            print("  2. Add concrete examples for each score level")
            print("  3. Use more specific language (avoid 'some', 'adequate')")
            print("  4. Test with different prompt formulations")

        elif kappa < 0.60:
            print(f"\n{dimension.upper()} - COULD BE IMPROVED")
            print(f"  Current kappa: {kappa:.3f}")
            print("  Suggestions:")
            print("  1. Clarify overlapping criteria")
            print("  2. Add discrimination examples")
            print("  3. Review low-agreement cases")

        else:
            print(f"\n{dimension.upper()} - GOOD ✓")
            print(f"  Current kappa: {kappa:.3f}")

def refined_rubric_v2():
    """
    Example of a refined rubric (v2) with clearer criteria
    """
    return {
        "completeness": {
            "description": "Does the summary capture all major points from the source?",
            "criteria": {
                5: "Includes 95%+ of major points; nothing critical omitted",
                4: "Includes 80-94% of major points; 1-2 minor omissions",
                3: "Includes 50-79% of major points; some important points missing",
                2: "Includes <50% of major points; critical points missing",
                1: "Misses almost all major points; severely incomplete"
            }
        },
        "accuracy": {
            "description": "Does the summary accurately represent the source without distortion?",
            "criteria": {
                5: "100% accurate; no factual errors or misrepresentations",
                4: "Accurate; may have 1 minor factual omission or nuance missing",
                3: "Mostly accurate; 1-2 factual errors or unclear statements",
                2: "Multiple factual errors (3+) or significant distortions",
                1: "Severely inaccurate; majority is incorrect or misleading"
            }
        },
        "conciseness": {
            "description": "Is the summary brief and to-the-point without unnecessary words?",
            "criteria": {
                5: "Highly efficient; no redundancy; reads as distilled summary",
                4: "Brief with minimal padding; mostly efficient",
                3: "Some unnecessary phrases; could be more concise",
                2: "Notably verbose; contains obvious redundancy",
                1: "Extremely verbose; reads like edited excerpt, not summary"
            }
        },
        "coherence": {
            "description": "Does the summary flow logically and read naturally?",
            "criteria": {
                5: "Excellent flow; logical structure; polished, natural prose",
                4: "Good coherence; mostly clear transitions",
                3: "Adequate flow; some awkward transitions",
                2: "Poor flow; confusing structure; disjointed transitions",
                1: "Incoherent; very difficult to follow"
            }
        },
        "relevance": {
            "description": "Does the summary focus on the most important information?",
            "criteria": {
                5: "Perfect prioritization; only essential information included",
                4: "Strong prioritization; mostly focuses on essential points",
                3: "Mix of essential and non-essential; some inflation",
                2: "Includes notable non-essential details",
                1: "Focuses on peripheral details; misses essential points"
            }
        }
    }

def save_refined_rubric():
    """Save improved rubric"""
    rubric = refined_rubric_v2()
    with open("rubric_v2.json", "w") as f:
        json.dump(rubric, f, indent=2)
    print("✓ Refined rubric saved to rubric_v2.json")

if __name__ == "__main__":
    # Load previous agreement results (from compute_agreement.py)
    try:
        with open("agreement_results.json") as f:
            agreement = json.load(f)
        suggest_rubric_improvements(agreement)
    except FileNotFoundError:
        print("Run compute_agreement.py first to generate agreement metrics")

    save_refined_rubric()
```

## Expected Output

### Console Output:
```
Running LLM Judge...

Judging 1/15...
Judging 2/15...
...
Judging 15/15...

======================================================================
AGREEMENT ANALYSIS: Human vs LLM Judge
======================================================================

COMPLETENESS
  Cohen's Kappa: 0.782 [Substantial]
  Mean Absolute Error: 0.40
  Correlation: 0.891 (p=0.0001)
  Human mean: 3.67
  LLM mean: 3.53

ACCURACY
  Cohen's Kappa: 0.805 [Almost Perfect]
  Mean Absolute Error: 0.33
  Correlation: 0.912 (p=0.0001)
  Human mean: 3.73
  LLM mean: 3.80

CONCISENESS
  Cohen's Kappa: 0.721 [Substantial]
  ...

======================================================================
OVERALL AGREEMENT: 0.762
======================================================================

======================================================================
CALIBRATION ANALYSIS
======================================================================

COMPLETENESS
  Human average: 3.67
  LLM average: 3.53
  Bias (LLM - Human): -0.14 [Well-calibrated]

ACCURACY
  Human average: 3.73
  LLM average: 3.80
  Bias (LLM - Human): +0.07 [Well-calibrated]
```

## Troubleshooting

### Issue: "API Key not found"
**Solution:**
```bash
# Create .env file with:
OPENAI_API_KEY=sk-xxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Then:
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: "Low agreement (kappa < 0.40)"
**Causes:**
- Rubric criteria are ambiguous
- Prompt doesn't clearly convey rubric
- Judge model too weak

**Solutions:**
1. Clarify rubric criteria with examples
2. Add few-shot examples to prompt
3. Try stronger model (gpt-4 vs gpt-3.5)
4. Increase temperature for diversity in reasoning

### Issue: "Inconsistent scores across runs"
**Solution:**
Use lower temperature (0.1-0.2) for consistency

## Extension Challenges

### Challenge 1: Pairwise Judge
**Difficulty:** 20 minutes

Create a judge that compares two summaries directly:

```python
def create_pairwise_prompt(source, summary_a, summary_b):
    """Ask LLM to compare two summaries"""
    return f"""Compare these two summaries of the text.

SOURCE:
{source}

SUMMARY A:
{summary_a}

SUMMARY B:
{summary_b}

Which is better? Explain why for completeness, accuracy, conciseness, coherence, and relevance.

Format:
BETTER: A or B
COMPLETENESS: [explanation]
ACCURACY: [explanation]
...
"""
```

### Challenge 2: Multi-Judge Panel
**Difficulty:** 25 minutes

Create an ensemble of judges and aggregate scores:

```python
def ensemble_judge(source, candidate, models=["gpt-4", "claude-3-opus"]):
    """Get scores from multiple judges and aggregate"""
    judges = [LLMJudge(model=m) for m in models]
    results = [judge.judge_summary(source, candidate) for judge in judges]

    # Aggregate
    avg_scores = {}
    for dim in ["completeness", "accuracy", "conciseness", "coherence", "relevance"]:
        scores = [r[dim] for r in results]
        avg_scores[dim] = sum(scores) / len(scores)

    return avg_scores
```

## Lab Completion Checklist

- [ ] Created evaluation rubric with 5 dimensions
- [ ] Created 20 test cases (5 docs × 3 quality levels each)
- [ ] Collected human labels for all test cases
- [ ] Implemented LLM judge using LiteLLM
- [ ] Computed Cohen's kappa for agreement
- [ ] Analyzed calibration (bias)
- [ ] Interpreted results and identified improvements
- [ ] Identified at least one rubric refinement
- [ ] Completed at least one extension challenge

## Summary

In this lab, you:
1. Designed a detailed evaluation rubric
2. Created a test dataset with gold labels
3. Implemented an LLM-based judge
4. Measured agreement with humans (Cohen's kappa)
5. Identified calibration issues
6. Iterated on the rubric

Key takeaways:
- LLMs can be reliable judges when given clear rubrics
- Agreement analysis (kappa) quantifies judge reliability
- Rubric clarity is critical for high agreement
- Calibration bias can be fixed through iteration
- Ensemble judges can improve robustness

**Time Spent:** Approximately 60 minutes including iterations
