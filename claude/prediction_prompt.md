**Your Role:** You are an expert analyst conducting a systematic literature review of AI trajectory forecasts. Your task is to extract explicit predictions in a structured format that will enable cross-document comparison.

---

## Document Context

**Document Title:** [TITLE]
**Author(s):** [AUTHORS]

---

## Your Task

Analyze this AI trajectory document and extract specific predictions following the guidelines below. This may be a long task if the document is complex, so take your time to think carefully before outputting your final structured analysis.

---

## WHAT COUNTS AS A PREDICTION?

**INCLUDE:**

- **Explicit forecasts**: "AI will achieve X by year Y" or "There's a Z% chance of outcome W"
- **Conditional predictions**: "If X continues, then Y will occur"
- **Scenario descriptions**: Detailed narratives of how specific futures could unfold
- **Mechanistic predictions**: "Process A will lead to outcome B through mechanism C"
- **Central implicit predictions**: Strong claims about what will/won't happen that are central to the document's argument

**EXCLUDE:**

- Pure normative claims without predictive content ("we should do X" - unless paired with "otherwise Y will happen")
- Historical claims about the past
- Pure definitions or conceptual frameworks
- General driver descriptions without specific outcomes (these are captured in driver extraction)

**GUIDELINE:** Predictions should be fairly explicit or clearly central to the document's argument. Always extract supporting evidence directly from the text - if you can't find textual evidence, it's probably too implicit to extract.

---

## GRANULARITY RULES

**Moderately Granular Approach:**

- Extract distinct predictions about **different outcomes** separately
- Extract distinct predictions about **different mechanisms** leading to the same outcome separately
- Extract predictions for **different scenarios** (optimistic vs pessimistic) separately
- **Consolidate** minor variations or restatements of the same prediction
- **Consolidate** if the same mechanism and outcome is discussed multiple times

**Example from "Gradual Disempowerment":**

- ✅ **Separate predictions:** "Labor share of GDP will decline toward zero", "AI systems may outcompete humans for scarce resources", "Humans may lose ability to meet basic needs"
- ✅ **Separate predictions:** "Economic displacement will occur gradually" vs "Economic displacement could lead to absolute disempowerment"
- ❌ **Don't separate:** Multiple mentions that "AI will replace human labor" - consolidate into one prediction with comprehensive evidence

---

## PREDICTION DIMENSIONS

### **Outcome Domains** (can be multiple)

- Economic
- Governance/Political
- Existential Risk
- AI Capabilities
- Social/Cultural
- Military/Security
- Other (specify)

### **Prediction Types**

- **Timeline**: When something will happen
- **Capability**: What AI will be able to do
- **Outcome**: What happens to world/humanity/institutions
- **Mechanism**: How a process will unfold
- **Probability**: Likelihood estimate of an event

### **Certainty Levels**

- **High**: Author treats as virtually certain, uses language like "will", "inevitable"
- **Medium**: Author treats as likely, uses language like "likely", "probably", "expect"
- **Low**: Author treats as possible but uncertain, uses language like "might", "could", "possibly"
- **Unclear**: Insufficient language to determine author's confidence level

### **Timeframes**

- Specific year/date
- Date range (e.g., "2030-2040")
- Relative period (e.g., "within next decade", "near-term", "eventually")
- "Unspecified"

---

## SPECIAL CASES

### **Nested/Conditional Predictions**

If a document presents a chain: "If A happens, then B will occur, leading to C"

**Extract as separate predictions:**

```json
{
  "prediction_id": "pred_001",
  "prediction_text": "A will happen",
  "depends_on": []
},
{
  "prediction_id": "pred_002",
  "prediction_text": "B will occur",
  "depends_on": ["pred_001"],
  "conditions": "Requires A to happen first"
},
{
  "prediction_id": "pred_003",
  "prediction_text": "C will result",
  "depends_on": ["pred_002"],
  "conditions": "Requires B to occur"
}
```

### **Scenario Branching**

If a document presents distinct scenarios without explicit labels:

- Extract each scenario's predictions as separate entries
- Don't create scenario labels unless document explicitly provides them
- Note in extraction_notes if document presents multiple distinct trajectories

### **Compound Predictions**

If a prediction has multiple distinct components:

- Extract as separate predictions if each component is substantial
- Use "depends_on" to link them if they're causally connected
- Consolidate if they're minor variations of the same claim

---

## EXTRACTION FORMAT

For each prediction, provide:

### **prediction_id**

Unique identifier: "pred_001", "pred_002", etc.

### **prediction_text**

Clear, concise statement of what is predicted (1-2 sentences max). Should be self-contained and understandable without context.

### **outcome_domain**

Array of applicable domains: ["Economic", "Existential Risk", ...]

### **prediction_type**

One of: "Timeline", "Capability", "Outcome", "Mechanism", "Probability"

### **timeframe**

When this is predicted to occur. Examples:

- "2030"
- "2030-2040"
- "Within next decade"
- "Near-term"
- "Eventually"
- "Unspecified"

### **certainty**

Author's confidence level: "High", "Medium", "Low", "Unclear"

### **certainty_language**

Key words/phrases indicating certainty: "will", "likely", "might", "could", "will likely", "almost certainly", etc.

### **is_conditional**

Boolean: Is this prediction dependent on specific conditions being met?

### **conditions**

If conditional, what needs to be true? (Otherwise: null or empty string)

### **mechanism**

How does the author think this will happen? Brief description of causal pathway (2-3 sentences max). Leave empty if not discussed.

### **depends_on**

Array of prediction_ids this depends on: ["pred_001", "pred_003"] or empty array []

### **evidence**

Supporting evidence from the document:

- Provide 1-3 representative quotes or detailed paraphrases
- Include section/page/chapter reference if available
- Keep total under 200 words per prediction
- Prioritize direct textual evidence

---

## OUTPUT FORMAT

First, **think out loud** about:

1. What are the main predictions or forecasts in this document?
2. Which predictions are explicit vs implicit?
3. Are there multiple scenarios or trajectories described?
4. Which predictions are conditional or part of causal chains?
5. How should I handle granularity - what should be consolidated vs separated?
6. What level of certainty does the author express about different predictions?

After your analysis, write **"EXTRACTED PREDICTIONS:"** and output a JSON object with this exact structure:

```json
{
  "document_title": "[Title]",
  "author": "[Author(s)]",
  "extraction_notes": "Important caveats about this extraction, multiple scenarios present, etc.",
  "predictions": [
    {
      "prediction_id": "pred_001",
      "prediction_text": "Clear statement of what is predicted",
      "outcome_domain": ["Economic", "Governance"],
      "prediction_type": "Outcome",
      "timeframe": "2030-2040",
      "certainty": "Medium",
      "certainty_language": "likely to occur",
      "is_conditional": false,
      "conditions": "",
      "mechanism": "Brief description of how author thinks this will happen",
      "depends_on": [],
      "evidence": "Direct quotes with references from the document"
    },
    {
      "prediction_id": "pred_002",
      "prediction_text": "Another prediction",
      "outcome_domain": ["Existential Risk"],
      "prediction_type": "Outcome",
      "timeframe": "Eventually",
      "certainty": "High",
      "certainty_language": "will inevitably",
      "is_conditional": true,
      "conditions": "If AI capabilities continue to advance without coordination",
      "mechanism": "",
      "depends_on": ["pred_001"],
      "evidence": "Quotes and references"
    }
  ]
}
```

---

## QUALITY CHECKS

Before finalizing, verify:

- ✅ Each prediction has clear textual evidence
- ✅ Predictions are moderately granular (not too broad, not too narrow)
- ✅ Similar predictions are consolidated
- ✅ Distinct outcomes/mechanisms are separated
- ✅ Dependencies ("depends_on") are used for causal chains
- ✅ Certainty levels match the author's language
- ✅ All predictions are fairly explicit or central to the argument

---

## DOCUMENT TO ANALYZE:

[full_doc_markdown]
