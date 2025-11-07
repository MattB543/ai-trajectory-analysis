# PREDICTION EXTRACTION PROMPT

You are analyzing an AI trajectory document to extract specific, falsifiable predictions. Your goal is to identify concrete forecasts that can be verified against future events.

## What Counts as a Prediction

**INCLUDE:**

- Specific, time-bound forecasts about future states or events
- Quantified probabilities or likelihoods
- Concrete capability milestones with timeframes
- Behavioral forecasts for specific actors
- Technical bottleneck predictions with timelines

**EXCLUDE:**

- General causal claims without timeframes ("compute drives progress")
- Vague assertions ("AI will be transformative")
- Recommendations or prescriptions (those go in recommendations)
- Historical statements or current facts
- Definitional statements

**Examples:**

- ✅ PREDICTION: "AGI will be achieved by 2027"
- ❌ NOT A PREDICTION: "AGI development is accelerating" (too vague, no timeframe)
- ✅ PREDICTION: "China will match US AI capabilities within 12 months of AGI"
- ❌ NOT A PREDICTION: "International competition will intensify" (no concrete verification criteria)

## Output Format

Return a JSON object with this exact structure:

```json
{
  "predictions": [
    {
      "pred_id": "pred_1",
      "prediction_text": "Clear, standalone statement of what will happen",
      "timeframe": "Specific time window (e.g., '2027-2028', 'by 2030', 'within 6 months of AGI')",
      "prediction_type": "One of the allowed types listed below",
      "confidence": "high | medium | low",
      "measurability": "clear | moderate | vague",
      "verification_criteria": "Specific conditions that would confirm this prediction came true",
      "conditional": "IF X THEN Y format, or null if unconditional",
      "quote": "Exact quote from document supporting this prediction"
    }
  ]
}
```

## Prediction Type Categories (USE EXACTLY THESE)

- **capability**: Predictions about what AI systems will be able to do (e.g., "surpass humans at all economically valuable work")
- **geopolitical**: International dynamics, competition, cooperation (e.g., "US-China AI race will intensify")
- **economic**: Market effects, GDP impact, job displacement, investment levels
- **technical_bottleneck**: What will limit or enable progress (e.g., "compute will remain primary bottleneck")
- **safety_alignment**: Progress on safety research, incident rates, alignment difficulty
- **deployment**: How AI will be deployed, adopted, or regulated
- **actor_behavior**: How specific actors (labs, governments, etc.) will behave

## Field-Specific Guidance

### prediction_text

- Write as a clear, standalone assertion
- Use consistent terminology (don't switch between "AGI" and "human-level AI")
- Be specific about what is being predicted
- Keep it concise (1-2 sentences max)

### timeframe

- Extract the specific time window the author gives
- If relative timing ("within X years of AGI"), preserve that phrasing
- If no explicit timeframe but clearly near-term, note "near-term (implied)"
- If genuinely vague, note "unspecified" but consider if it's really a prediction

### confidence

- **high**: Author states high confidence, uses strong language ("will", "certainly", ">70%")
- **medium**: Moderate hedging ("likely", "probably", "40-60%")
- **low**: Heavy hedging ("might", "could", "possible", "<30%")
- Base this on the author's language, not your assessment

### measurability

- **clear**: Specific metrics, benchmarks, or observable events (e.g., "passes all coding interviews")
- **moderate**: Somewhat concrete but requires interpretation (e.g., "transformative impact on economy")
- **vague**: Hard to verify objectively (e.g., "significant progress")

### verification_criteria

- Be specific about how we'd know if this came true
- Reference benchmarks, metrics, or observable events where possible
- Examples:
  - "AI system scores >95% on GPQA benchmark"
  - "US implements compute export controls"
  - "GDP growth exceeds 10% annually"
  - "Major lab announces AGI achievement accepted by research community"

### conditional

- Extract IF-THEN structure if present
- Write in format: "IF [condition] THEN [this prediction follows]"
- Set to null if the prediction is stated unconditionally
- Examples:
  - "IF algorithmic progress stalls"
  - "IF US maintains compute advantage"
  - "IF no major regulatory intervention"

### quote

- Provide the exact text that supports this prediction
- Include enough context to understand it standalone
- If prediction is synthesized from multiple sentences, include all relevant parts
- Keep quotes concise but complete

## Quality Standards

1. **Accuracy**: Every prediction must be directly supported by document text
2. **Completeness**: Extract 10-25 predictions per document (adjust for document length)
3. **Distinctness**: Each prediction should be meaningfully different - don't extract minor variations
4. **Specificity**: Favor concrete, falsifiable predictions over vague ones
5. **Consistency**: Use the same terminology and style across all predictions

## Special Cases

**Quantified probabilities**: If author gives specific probability (e.g., "30% chance of X"), include that in prediction_text

**Scenario-dependent predictions**: If author presents multiple scenarios with different predictions, extract each as a separate conditional prediction

**Implicit predictions**: If strongly implied but not explicitly stated, you may extract it but note in verification_criteria that it's implied

**Ranges**: If prediction gives a range (e.g., "AGI between 2027-2035"), preserve the full range in timeframe

## Before You Begin

1. Read the entire document first to understand context
2. Focus on the author's distinctive forecasts, not general background
3. Err on the side of being too specific rather than too vague
4. When in doubt about categorization, choose the most specific prediction_type that fits

## Document Text

${document}
