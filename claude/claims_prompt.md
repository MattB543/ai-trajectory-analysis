# AI Trajectory Document Analysis: Claim Extraction Task

## Your Mission

You are conducting a systematic literature review of major AI trajectory documents. Your task is to extract ALL significant claims, predictions, and recommendations from the document provided below.

These extractions will be compared across 20+ documents to identify areas of agreement and disagreement in the AI safety/governance field. **Consistency and precision are critical.**

## What to Extract

Extract claims that are:

- ✅ **Specific and substantive** - someone could meaningfully agree or disagree
- ✅ **Distinctive to the author** - represents their particular position or analysis
- ✅ **Falsifiable or debatable** - not just definitions or obvious background facts
- ✅ **Action-relevant** - could influence decision-making or strategy

**Do NOT extract:**

- ❌ Pure definitions (e.g., "AGI means artificial general intelligence")
- ❌ Obvious historical facts (e.g., "Deep learning became dominant in the 2010s")
- ❌ Vague truisms (e.g., "AI is important" or "we should be careful")
- ❌ Examples or illustrations used to support a claim (extract the claim itself instead)
- ❌ Rhetorical questions unless they clearly imply a position

## Claim Types (use exactly these categories)

**timeline** - Predictions about when capabilities or events will occur

- Example: "AGI will likely arrive between 2027-2030"

**capability** - Claims about what AI systems will/won't be able to do

- Example: "Models will achieve human-level performance on all cognitive tasks"

**risk** - Assertions about dangers, failure modes, or bad outcomes

- Example: "Misalignment poses an existential threat to humanity"

**strategic** - Recommendations about what actors should do

- Example: "The US should maintain a decisive strategic advantage in AI"

**causal** - Claims about what causes what, necessary conditions, or dependencies

- Example: "Compute scaling is the primary driver of capability gains"

**actor_behavior** - Predictions about how organizations/countries will act

- Example: "China will not agree to international compute governance"

**feasibility** - Claims about whether something is possible/tractable

- Example: "Technical AI alignment is solvable with current paradigms"

**priority** - Arguments about what matters most or deserves focus

- Example: "Governance is more important than technical alignment work"

**other** - Significant claims that don't fit above categories (use sparingly)

## Confidence Levels

Infer the author's confidence from their language:

**high** - Stated with certainty, strong conviction, or minimal hedging

- Indicators: "will", "certainly", "definitely", "clearly", "without doubt"
- Example: "AGI will arrive this decade"

**medium** - Qualified predictions, likely but uncertain

- Indicators: "probably", "likely", "expect", "anticipate", "plausible"
- Example: "AGI will probably arrive by 2030"

**low** - Highly uncertain, speculative, or heavily hedged

- Indicators: "might", "possibly", "unclear", "hard to say", "could"
- Example: "AGI might arrive by 2030, though this is highly uncertain"

If the author doesn't clearly indicate confidence, use your best judgment based on tone and hedging language.

## Handling Conditional Claims

Many claims are conditional (e.g., "IF short timelines, THEN governance is intractable"). Format these as:

```json
{
  "claim_text": "Governance becomes intractable under short timeline scenarios",
  "conditional": "IF AGI arrives before 2030",
  ...
}
```

Include the conditional context so the claim remains interpretable standalone.

## Handling Implicit Claims

Authors often imply positions without stating them directly. Extract these IF they're clear and central to the argument:

- Author spends pages arguing for X → Extract "X is true/important"
- Author dismisses concern Y in passing → Extract "Y is not a significant risk"
- Author's recommendations only make sense if Z → Extract Z as an implicit assumption

## Output Format

Return a JSON object with this exact structure:

```json
{
  "claims": [
    {
      "claim_id": "1",
      "claim_type": "timeline",
      "claim_text": "AGI will likely arrive between 2027 and 2030",
      "confidence": "high",
      "quote": "The exact quote from the document that supports this claim",
      "conditional": "IF current trends continue" (or null if unconditional),
      "notes": "Brief context if needed for interpretation" (optional)
    },
    {
      "claim_id": "2",
      ...
    }
  ]
}
```

## Quality Standards

**Claim Text Requirements:**

- Write as standalone assertions that make sense out of context
- Use consistent terminology (always "AGI" not switching between "AGI/superintelligence/transformative AI")
- Be specific - include numbers, timeframes, and concrete details from the document
- Use the author's framing and language where possible
- Keep it concise but complete (aim for 1-2 sentences max)

**Quote Requirements:**

- Must be verbatim from the document
- Should directly support the claim
- Can be a phrase or full sentence(s)
- Use "..." for omitted text if needed

**Coverage:**

- Extract 20-40 claims for a typical essay-length document
- More for longer reports (aim for comprehensive coverage)
- Include claims the author emphasizes repeatedly
- Include claims mentioned only briefly if they're substantive

## Examples

**Good Extraction:**

```json
{
  "claim_id": "15",
  "claim_type": "timeline",
  "claim_text": "AGI will most likely be developed by 2027, with significant probability of arrival between 2025-2030",
  "confidence": "high",
  "quote": "by 2027, it will be clear that AGI is imminent... the probability mass is heavily concentrated in 2025-2030",
  "conditional": null,
  "notes": null
}
```

**Bad Extraction (too vague):**

```json
{
  "claim_text": "AGI is coming soon",
  ...
}
```

**Good Extraction:**

```json
{
  "claim_id": "23",
  "claim_type": "strategic",
  "claim_text": "The US government should establish a compute governance regime including chip export controls and data center oversight",
  "confidence": "high",
  "quote": "We need a compute governance regime—export controls, monitoring of large training runs, security requirements for frontier AI datacenters",
  "conditional": null,
  "notes": null
}
```

**Good Extraction (conditional):**

```json
{
  "claim_id": "31",
  "claim_type": "feasibility",
  "claim_text": "International coordination on AI governance is intractable under short timeline scenarios",
  "confidence": "medium",
  "quote": "if we only have a few years, the international coordination problem becomes much harder",
  "conditional": "IF AGI timeline is less than 5 years",
  "notes": null
}
```

## Final Checklist

Before submitting your extraction, verify:

- All claims are substantive and debatable
- Claim text is self-contained and specific
- Quotes are verbatim and properly support claims
- Confidence levels are inferred from textual evidence
- Conditional claims are properly marked
- Claim types use only the specified categories
- JSON is valid and follows the schema exactly
- You've aimed for comprehensive coverage (didn't miss major arguments)

## The Document to Analyze

${document}
