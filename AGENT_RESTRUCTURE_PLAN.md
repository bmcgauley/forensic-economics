# Agent Structure Restructure Plan

## Current Problems

### 1. Unstructured LLM Outputs
**Example issue:** LLM producing conversational text
```
"Okay, here's an analysis of the worklife expectancy data, presented as a
forensic economic report, aiming for a professional and insightful assessment:

"Based on the Skoog Table data, the victim's projected worklife years..."
```

**Root cause:** Using `generate_completion()` without JSON mode or schema enforcement.

### 2. Missing Agents
Based on the system diagram, we need:
- **Person Investigation Agent** - Initial data collection and validation
- Potentially an **Earnings Projections Agent** separate from wage growth

### 3. Incorrect Agent Ordering
**Current order in supervisor:**
1. FedRateAgent
2. SkoogTableAgent
3. LifeExpectancyAgent
4. WorklifeExpectancyAgent
5. WageGrowthAgent
6. DiscountRateAgent
7. PresentValueAgent

**Required order (from diagram):**
1. **PersonInvestigationAgent** (NEW) - Validate and enrich person data
2. FedRateAgent - Get interest rates
3. LifeExpectancyAgent - Calculate life expectancy
4. SkoogTableAgent - Get worklife data
5. WorklifeExpectancyAgent - Calculate remaining work years
6. WageGrowthAgent - Project salary growth
7. DiscountRateAgent - Determine discount rates
8. PresentValueAgent - Calculate final economic loss

### 4. No Schema Validation
AI agents output freeform text that gets embedded in JSON, leading to:
- Template variables not being replaced (e.g., `{work id}`)
- Conversational preambles
- Inconsistent formatting
- Parsing failures

## Solution: Structured I/O with Pydantic Schemas

### Phase 1: Create Schema Definitions

Create `src/agents/schemas.py` with Pydantic models for all agent I/O:

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class AgentInput(BaseModel):
    """Base class for agent inputs"""
    pass


class AgentOutput(BaseModel):
    """Base class for agent outputs"""
    pass


class PersonInvestigationInput(AgentInput):
    victim_age: int = Field(..., ge=0, le=120)
    victim_sex: str = Field(..., pattern="^(M|F|male|female)$")
    occupation: str
    education: str
    location: str = "US"
    salary: float = Field(..., gt=0)


class PersonInvestigationOutput(AgentOutput):
    validated_age: int
    normalized_sex: str  # M or F
    occupation_soc_code: Optional[str]
    education_level: str
    location_jurisdiction: str
    validated_salary: float
    validation_notes: List[str]


class AIAnalysisOutput(BaseModel):
    """Structured AI analysis output"""
    key_findings: List[str] = Field(..., max_items=5)
    risk_factors: List[str] = Field(..., max_items=3)
    assumptions: List[str] = Field(..., max_items=3)
    confidence_level: str = Field(..., pattern="^(high|medium|low)$")
    recommendation: str = Field(..., max_length=500)


class WageGrowthOutput(AgentOutput):
    annual_growth_rate: float
    growth_rate_series: List[float]
    projected_wages_by_year: Dict[int, float]
    ai_analysis: AIAnalysisOutput  # STRUCTURED instead of freeform text
    ai_model: str


class WorklifeExpectancyOutput(AgentOutput):
    worklife_years: float
    retirement_age: int
    worklife_years_by_age: Dict[int, float]
    ai_analysis: AIAnalysisOutput  # STRUCTURED
    ai_model: str


class DiscountRateOutput(AgentOutput):
    recommended_discount_rate: float
    discount_curve: List[float]
    methodology: str
    treasury_rate: float
    ai_analysis: AIAnalysisOutput  # STRUCTURED
    ai_model: str
```

### Phase 2: Update Ollama Client for JSON Mode

Modify `src/utils/ollama_client.py`:

```python
def generate_structured_completion(
    self,
    prompt: str,
    system_prompt: str,
    schema: Dict[str, Any],
    temperature: float = 0.3  # Lower for more consistent JSON
) -> Dict[str, Any]:
    """
    Generate a structured JSON completion with schema enforcement.

    Args:
        prompt: The prompt text
        system_prompt: System prompt for context
        schema: JSON schema dict for output validation
        temperature: Sampling temperature (lower = more consistent)

    Returns:
        Parsed JSON dict matching the schema
    """
    # Add schema instructions to prompt
    schema_str = json.dumps(schema, indent=2)

    enhanced_prompt = f"""{prompt}

CRITICAL: You MUST respond with ONLY valid JSON matching this exact schema:

{schema_str}

RULES:
1. Output ONLY the JSON object, no preamble, no explanation
2. Do NOT include markdown code fences like ```json
3. All fields in the schema are REQUIRED
4. String arrays must have the exact number of items specified
5. Follow the pattern constraints exactly

Begin your JSON response now:"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': enhanced_prompt}
    ]

    # Make API call
    response = self.chat(messages, temperature=temperature)
    response_text = response['message']['content'].strip()

    # Try to extract JSON if there's extra text
    try:
        # First try direct parse
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown or surrounding text
        import re

        # Remove markdown code fences
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()

        # Try to find JSON object
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
```

### Phase 3: Create Person Investigation Agent

Create `src/agents/person_investigation_agent.py`:

```python
"""
Person Investigation Agent

Purpose: Validate and enrich initial person data entry
Inputs: Raw victim data from user intake
Outputs: Validated and normalized person data
Role: Data Validation & Enrichment

Single-file agent (target <=300 lines)
"""

from datetime import datetime
from typing import Dict, Any
import re


class PersonInvestigationAgent:
    """Agent for validating and enriching person investigation data."""

    def __init__(self):
        """Initialize the agent."""
        pass

    def run(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize person data.

        Args:
            input_json: Dictionary containing:
                - victim_age (int): Age of victim
                - victim_sex (str): Gender (M/F/male/female)
                - occupation (str): Occupation or SOC code
                - education (str): Education level
                - location (str): Jurisdiction code
                - salary (float): Annual salary

        Returns:
            Dictionary containing validated and enriched data
        """
        provenance_log = []

        # Extract inputs
        victim_age = input_json.get('victim_age')
        victim_sex = input_json.get('victim_sex', '').lower()
        occupation = input_json.get('occupation')
        education = input_json.get('education')
        location = input_json.get('location', 'US')
        salary = input_json.get('salary')

        provenance_log.append({
            'step': 'input_received',
            'description': 'Raw person data received for validation',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'victim_age': victim_age,
                'victim_sex': victim_sex,
                'occupation': occupation,
                'education': education,
                'location': location,
                'salary': salary
            }
        })

        validation_notes = []

        # Normalize sex
        if victim_sex in ['m', 'male']:
            normalized_sex = 'M'
        elif victim_sex in ['f', 'female']:
            normalized_sex = 'F'
        else:
            normalized_sex = 'M'  # Default
            validation_notes.append(f"Invalid sex '{victim_sex}', defaulting to 'M'")

        # Validate age
        if victim_age < 0 or victim_age > 120:
            validation_notes.append(f"Age {victim_age} is out of valid range (0-120)")

        # Validate salary
        if salary <= 0:
            validation_notes.append(f"Salary {salary} is not positive")

        # Attempt to parse SOC code from occupation
        soc_code = None
        soc_pattern = r'\b\d{2}-\d{4}\b'
        if re.match(soc_pattern, occupation):
            soc_code = occupation
            validation_notes.append(f"Occupation appears to be SOC code: {soc_code}")

        provenance_log.append({
            'step': 'data_validation',
            'description': 'Validated and normalized person data',
            'formula': None,
            'source_url': None,
            'source_date': datetime.utcnow().isoformat(),
            'value': {
                'normalized_sex': normalized_sex,
                'soc_code': soc_code,
                'validation_notes': validation_notes
            }
        })

        return {
            'agent_name': 'PersonInvestigationAgent',
            'inputs_used': input_json,
            'outputs': {
                'validated_age': victim_age,
                'normalized_sex': normalized_sex,
                'occupation_soc_code': soc_code,
                'education_level': education,
                'location_jurisdiction': location,
                'validated_salary': salary,
                'validation_notes': validation_notes
            },
            'provenance_log': provenance_log
        }
```

### Phase 4: Update Existing AI Agents

For each AI agent (WageGrowthAgent, WorklifeExpectancyAgent, DiscountRateAgent):

1. Define a JSON schema for the AI analysis output
2. Use `generate_structured_completion()` instead of `generate_completion()`
3. Validate the response against the schema
4. Return structured data instead of freeform text

**Example for WageGrowthAgent:**

```python
# Define the schema
AI_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "key_findings": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 3,
            "description": "2-3 key findings about wage growth"
        },
        "risk_factors": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 2,
            "description": "1-2 risk factors to consider"
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 2,
            "description": "1-2 key assumptions"
        },
        "confidence_level": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Confidence in the projection"
        },
        "recommendation": {
            "type": "string",
            "maxLength": 300,
            "description": "Brief recommendation for the calculation"
        }
    },
    "required": ["key_findings", "risk_factors", "assumptions", "confidence_level", "recommendation"]
}

# In the run() method, replace the LLM call:
ai_prompt = f"""Analyze wage growth projection for forensic economics case.

CASE DATA:
- Occupation: {occupation}
- Current Salary: ${salary:,.2f}
- Education: {education}
- Growth Rate: {adjusted_growth_rate*100:.2f}%

Provide structured analysis with:
- 2-3 key findings about the wage growth projection
- 1-2 risk factors to consider
- 1-2 key assumptions made
- Confidence level (high/medium/low)
- Brief recommendation (max 300 chars)"""

try:
    ai_analysis_json = self.llm.generate_structured_completion(
        prompt=ai_prompt,
        system_prompt="You are a forensic economist analyzing wage growth.",
        schema=AI_ANALYSIS_SCHEMA,
        temperature=0.3
    )

    ai_analysis = ai_analysis_json  # Now it's a structured dict, not text

except Exception as e:
    # Fallback to structured default
    ai_analysis = {
        "key_findings": [
            f"Projected growth rate of {adjusted_growth_rate*100:.2f}% based on BLS data",
            f"Education level ({education}) supports growth assumptions"
        ],
        "risk_factors": [
            "Economic conditions may vary from historical averages"
        ],
        "assumptions": [
            "Historical wage growth patterns continue",
            "Occupation remains stable"
        ],
        "confidence_level": "medium",
        "recommendation": "Growth rate is reasonable based on historical data"
    }
```

### Phase 5: Update Supervisor Agent Order

Modify [supervisor_agent.py](src/agents/supervisor_agent.py:104-241) to match the required flow:

```python
# === AGENT 1: Person Investigation Agent ===
person_result = self._run_agent(
    agent=self.person_investigation_agent,
    agent_index=0,
    input_data=intake,
    description='Validating and enriching person data'
)
agent_results.append(person_result)

# Use validated data for subsequent agents
validated_data = {
    **intake,
    'victim_sex': person_result['outputs']['normalized_sex'],
    'soc_code': person_result['outputs']['occupation_soc_code']
}

# === AGENT 2: Federal Reserve Rate Agent ===
fed_rate_result = self._run_agent(...)

# === AGENT 3: Life Expectancy Agent ===
life_result = self._run_agent(
    agent=self.life_expectancy_agent,
    agent_index=2,
    input_data=validated_data,  # Use validated data
    description='Calculating life expectancy from CDC tables'
)

# Continue with rest of agents in correct order...
```

## Implementation Priority

1. **HIGH PRIORITY** - Update Ollama client with `generate_structured_completion()`
2. **HIGH PRIORITY** - Create Person Investigation Agent
3. **HIGH PRIORITY** - Update WageGrowthAgent, WorklifeExpectancyAgent, DiscountRateAgent to use structured output
4. **MEDIUM PRIORITY** - Update Supervisor agent ordering
5. **LOW PRIORITY** - Create Earnings Projections agent (if needed separately from wage growth)

## Testing Plan

1. Test each agent individually with structured I/O
2. Test supervisor agent with new ordering
3. Verify no template variables in output
4. Validate all JSON outputs parse correctly
5. Run end-to-end test with sample case

## Benefits

1. ✅ **Predictable outputs** - No more conversational text or template variables
2. ✅ **Type safety** - Pydantic schemas enforce correct data types
3. ✅ **Validation** - Catch errors early before they propagate
4. ✅ **Better debugging** - Clear error messages when schemas don't match
5. ✅ **Correct agent flow** - Matches system diagram requirements
