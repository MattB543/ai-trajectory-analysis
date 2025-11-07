You are analyzing an AI trajectory document to extract all strategic recommendations in a systematic, structured format.

# TASK

Extract every recommendation the author makes about what should be done, by whom, and when. Output valid JSON.

# OUTPUT FORMAT

Return a JSON object with a "recommendations" array:

{
"recommendations": [
{
"rec_id": "unique identifier (e.g., rec_1, rec_2)",
"action": "specific, concrete action being recommended",
"actor": "who should take this action",
"target_timeline": "when this should happen",
"urgency": "critical | high | medium | low",
"goal": "what outcome this is meant to achieve",
"conditions": "any conditions under which this applies, or 'unconditional'",
"rationale_summary": "brief explanation of why the author recommends this",
"quote": "direct quote from document supporting this recommendation"
}
]
}

# FIELD DEFINITIONS

**rec_id**: Simple sequential identifier (rec_1, rec_2, rec_3, etc.)

**action**: The specific thing being recommended. Must be:

- Concrete and actionable (avoid vague statements like "think about X")
- Stated as a clear imperative (e.g., "Establish compute governance framework", "Pause frontier AI development", "Invest $10B in alignment research")
- Specific enough that someone could act on it

**actor**: Who should take this action. Options include:

- "US Government" / "Chinese Government" / "Governments" (international)
- "AI labs" (all labs) / "Frontier AI labs" / specific lab names
- "AI safety researchers" / "ML researchers" / "Academia"
- "Private sector" / "Industry"
- "International community" / "UN" / specific institutions
- "Everyone" / "Society" / "Public"
- Be specific when the author is specific; use broader categories when they speak generally

**target_timeline**: When should this happen? Use author's language when present:

- "immediately" / "urgently" / "ASAP"
- "before AGI" / "before 2027" / "by 2030"
- "within 2 years" / "next 5 years"
- "now" / "starting now"
- "ongoing" (for continuous actions)
- "unclear" (if author doesn't specify)

**urgency**: Author's implied or explicit sense of how critical this is:

- "critical": Existential importance, must happen or catastrophe likely
- "high": Very important, significant consequences if not done
- "medium": Important but not existential
- "low": Nice to have, marginal improvement
  Infer from context if not explicitly stated.

**goal**: What is this recommendation trying to achieve? Common goals:

- "prevent AI misalignment" / "solve alignment"
- "prevent misuse" / "reduce catastrophic risks"
- "slow AI progress" / "buy more time"
- "enable international coordination"
- "maintain US advantage" / "prevent China from leading"
- "improve safety standards"
- "increase public awareness"
  Be specific about what outcome the author wants.

**conditions**: Under what circumstances does this apply?

- "unconditional" (if author recommends this regardless)
- "IF short timelines (before 2030)"
- "IF alignment is hard"
- "IF we have unipolar scenario"
- "IF compute remains bottleneck"
- "ONLY IF coordinated internationally"
  Capture any explicit or implicit conditions.

**rationale_summary**: In 1-2 sentences, why does the author recommend this? What's their logic?

- Connect to their worldview/assumptions
- Explain the causal chain (doing X leads to Y which achieves goal Z)

**quote**: Direct quote from the document that best captures this recommendation.

- Should be the most explicit statement of the recommendation
- Include enough context to be meaningful
- 1-3 sentences typically

# WHAT TO EXTRACT

**DO extract:**

- Explicit recommendations (author says "we should", "I recommend", "it's critical that")
- Implicit recommendations (author argues strongly for why something needs to happen)
- Policy proposals
- Research directions that should be prioritized
- Actions that actors should take or avoid
- Strategic advice
- Governance proposals

**DO NOT extract:**

- Predictions without recommendations (just saying what will happen)
- Descriptions of what IS happening (only what SHOULD happen)
- Background context or scene-setting
- Obvious platitudes ("we should care about safety")
- Historical examples unless framed as lessons to apply

# QUALITY STANDARDS

1. **Completeness**: Extract 15-50 recommendations per document depending on length. Don't miss major recommendations, but don't inflate the count with trivial ones.

2. **Specificity**: Each recommendation should be distinct. Don't extract slight variations as separate recommendations. But DO separate if actor, timeline, or goal differs.

3. **Consistency**: Use consistent terminology across recommendations:

   - Always "AGI" not mixing "AGI/transformative AI/superintelligence"
   - Always "US Government" not mixing "US/America/Washington"
   - Always "AI labs" not mixing "labs/companies/developers"

4. **Accuracy**: Stay true to author's intent. Don't over-interpret or editorialize.

5. **Actionability**: Someone reading just the "action" field should understand what to do.

# EXAMPLES

Good recommendation:
{
"rec_id": "rec_1",
"action": "Implement mandatory safety evaluations for training runs above 10^26 FLOP",
"actor": "US Government",
"target_timeline": "before 2027",
"urgency": "critical",
"goal": "prevent unauthorized AGI development and ensure visibility into frontier AI progress",
"conditions": "IF current pace continues and AGI likely by 2027-2030",
"rationale_summary": "Without government visibility into large training runs, rogue actors or careless labs could develop AGI without adequate safety measures. Compute is currently the primary bottleneck and thus the most viable point of control.",
"quote": "The government needs to ensure it has visibility into any training run that could potentially produce AGI-level systems. This means mandatory reporting above 10^26 FLOP."
}

Poor recommendation (too vague):
{
"action": "Think more about safety",
"actor": "Everyone",
"goal": "Make things better"
}

# EDGE CASES

- If a recommendation has multiple distinct actors, create separate entries
- If the same action is recommended for different scenarios, create separate entries with different conditions
- If author lists sub-recommendations under a broader recommendation, extract each sub-recommendation separately
- If uncertain about urgency or timeline, use your best judgment based on surrounding context
- If a recommendation is implied but not explicit, extract it but note this in rationale_summary

# OUTPUT REQUIREMENTS

- Valid JSON only, no markdown formatting
- No explanatory text before or after the JSON
- Ensure all quotes are properly escaped
- Use double quotes throughout
- If a field is unknown/unclear, use "unclear" or "not specified" rather than omitting

Now extract all recommendations from the following document:

${document}
