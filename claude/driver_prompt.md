# AI Trajectory Driver Extraction Prompt

**Your Role:** You are an expert analyst conducting a systematic literature review of AI trajectory forecasts. Your task is to extract key drivers in a structured format that will enable cross-document comparison.

---

## Document Context

**Document Title:** [TITLE]
**Author(s):** [AUTHORS]

---

## Your Task

Analyze this AI trajectory document and extract key drivers following the guidelines below. This may be a long task if the document is complex, so take your time to think carefully before outputting your final structured analysis.

---

## EXTRACTION APPROACH

### **PRIMARY TASK:** Identify Predefined Drivers

Review the document for mentions of the specific drivers listed in the "Predefined Driver List" below. These 20+ drivers represent the most common factors across AI trajectory literature.

### **SECONDARY TASK:** Identify Custom Drivers (If Needed)

If the document emphasizes important drivers NOT captured in the predefined list, you may add custom drivers. Label these as:

- **"Custom: [Driver Name]"**
- Provide extra justification for why this driver deserves separate extraction

**Guideline:** Prefer the predefined drivers when possible. Only add custom drivers for truly distinctive or heavily emphasized factors that don't fit existing categories.

### **Consolidation Rule**

If a driver appears multiple times in the document:

- **Default:** Consolidate into ONE entry with a comprehensive description covering all mentions
- **Exception:** If the document presents the SAME driver with contradictory perspectives or in distinctly different scenarios, create separate entries:
  - "Driver Name (Scenario A)"
  - "Driver Name (Optimistic Case)"
  - "Driver Name (Pessimistic Case)"

---

## DRIVER CATEGORIES

There are 7 high-level driver categories:

1. **Technological** - Technical capabilities, compute, algorithms, tools
2. **Organizational** - Lab dynamics, competition, development strategies
3. **Governance** - Regulation, coordination, institutional design
4. **Societal** - Public trust, acceptance, social dynamics
5. **Safety & Alignment** - Technical alignment challenges and approaches
6. **Geopolitical** - International competition, arms races, power dynamics
7. **Economic** - Market forces, automation, productivity, incentives

**Note:** Not every document will have drivers in all categories. Some documents may focus heavily on 2-3 categories and have nothing to say about others. This is expected.

---

## PREDEFINED DRIVER LIST

### **TECHNOLOGICAL DRIVERS**

1. **Compute Scaling and Hardware Advances**

   - Exponential growth in computational power (Moore's Law), data center expansion, chip advances enabling continued AI progress through scaling.

2. **Algorithmic Innovations and Breakthroughs**

   - Fundamental advances in ML methods, architectures (transformers, etc.), training approaches, and techniques beyond raw compute scaling.

3. **Transparency and Interpretability Tools**

   - Technologies to understand AI internal states, detect deception, explain decisions, and enable meaningful oversight.

4. **Defense-Favoring AI Capabilities**
   - AI technologies that enhance defensive capabilities in cybersecurity, verification, alignment testing, and threat detection.

### **ORGANIZATIONAL DRIVERS**

5. **Lab Safety and Security Culture**

   - Organizational practices around AI safety, security protocols, risk assessment, and internal governance within AI development organizations.

6. **Inter-Lab Competition**

   - Competitive dynamics between AI labs (OpenAI, Anthropic, DeepMind, etc.) creating pressure to prioritize speed and capabilities over safety considerations.

7. **Open Source vs. Closed Development Strategies**

   - Tension between open-sourcing AI models/research for democratization versus keeping them proprietary for safety and control.

8. **Institutional Learning and Adaptation**

   - Organizations' and society's capacity to identify failures, update beliefs, modify systems, and adapt to rapid AI-driven changes.

9. **Corporate AI Competition and Lobbying**
   - Private companies resisting regulation, lobbying for favorable policies, and pursuing profit maximization potentially at odds with safety.

### **GOVERNANCE DRIVERS**

10. **International Coordination Challenges**

    - Difficulties achieving global cooperation on AI governance, safety standards, development controls, and policy harmonization.

11. **Hybrid Governance Structures**

    - Institutional designs combining AI computational power with human judgment, accountability, and meaningful oversight mechanisms.

12. **Surveillance and Control Capabilities**

    - AI-enabled comprehensive monitoring, behavior prediction, and social control mechanisms (both risks and potential governance tools).

13. **Cross-System Power Dynamics**
    - How cultural, state, and economic powers mutually shape each other across institutional boundaries in the AI age.

### **SOCIETAL DRIVERS**

14. **Public Trust and Acceptance**
    - Societal trust in AI technologies, information integrity, and institutions, affecting adoption rates, governance legitimacy, and social stability.

### **SAFETY & ALIGNMENT DRIVERS**

15. **General Alignment Problem Difficulty**

    - The fundamental challenge of ensuring AI systems reliably pursue human-intended goals across capability levels.

16. **Deceptive Alignment Risks**

    - Risk of AI systems appearing aligned during training/testing while hiding misaligned goals, particularly at deployment or higher capability levels.

17. **Value Alignment Strategies**

    - Different technical approaches to aligning AI with human values: RLHF, constitutional AI, debate, amplification, etc.

18. **Human Oversight Limitations at Scale**
    - Fundamental inability of humans to meaningfully oversee AI systems operating at superhuman speed, scale, and complexity.

### **GEOPOLITICAL DRIVERS**

19. **US-China AI Competition**

    - Intense technological rivalry between the US and China as leading nations in AI development, affecting timelines, safety priorities, and governance.

20. **International AI Arms Race Dynamics**

    - Multiple nations racing to develop AI first for economic and military advantage, creating unstable competitive pressures and coordination failures.

21. **Corporate/Economic Power Influencing Governance**
    - How concentrated economic power enables corporations to shape regulations, policies, and cultural attitudes in their favor.

### **ECONOMIC DRIVERS**

22. **Winner-Take-All Competitive Dynamics**

    - Economic forces creating concentration of AI capabilities and competitive pressure to reduce human involvement for efficiency.

23. **Declining Costs in AI and Computing**

    - Exponential reduction in computational costs making AI increasingly affordable, accessible, and ubiquitous.

24. **Productivity Gains from AI**

    - Empirically demonstrated productivity increases across sectors from AI tools, accelerating economic transformation and adoption.

25. **Economic Automation and Labor Market Transformation**
    - AI's ability to automate cognitive work, fundamentally reshaping employment, income distribution, productivity, and economic structures.

---

## EXTRACTION FORMAT

For each driver identified, provide:

### **driver_name**

The specific driver from the predefined list (or "Custom: [Name]" if adding a new one)

### **description**

1-3 sentences describing how THIS document discusses this driver. Not a generic definition, but the document's specific perspective, emphasis, or framing.

### **direction**

How this driver affects the trajectory. Be specific and nuanced. Examples:

- "Accelerates AI capabilities development significantly"
- "Increases catastrophic risk while accelerating capabilities"
- "Decelerates development through regulatory friction"
- "Bidirectional: Could increase safety if implemented well, or create false confidence if done poorly"
- "Increases likelihood of positive outcomes by enabling coordination"

### **magnitude**

How important is this driver according to the document?

- **High** - Central to the document's argument, frequently discussed, major implications
- **Medium** - Important but not central, discussed in some depth
- **Low** - Mentioned but not emphasized, minor role in the trajectory

### **certainty**

How does the document treat this driver?

- **Certain** - Treated as given, inevitable, or already happening
- **Likely** - Expected to occur with high probability
- **Uncertain** - Could go multiple ways, key variable with unknown outcome
- **Contested** - Document acknowledges disagreement or presents multiple views

### **evidence**

Supporting evidence from the document:

- Provide 1-3 representative quotes or detailed paraphrases
- Include section/page/chapter reference if available
- Keep total evidence under 200 words per driver
- Prioritize clarity and representativeness over comprehensiveness

---

## OUTPUT FORMAT

First, **think out loud** about:

1. What are the main themes and arguments of this document?
2. Which driver categories seem most relevant?
3. Which specific predefined drivers appear prominently?
4. Are there any important drivers NOT captured in the predefined list?
5. How should ambiguous cases be handled?

After your analysis, write **"KEY DRIVERS:"** and output a JSON object with this exact structure:

```json
{
  "document_title": "[Title]",
  "extraction_notes": "Any important caveats or notes about this extraction",
  "drivers": {
    "technological": [
      {
        "driver_name": "Compute Scaling and Hardware Advances",
        "description": "The document's specific discussion of this driver in 1-3 sentences",
        "direction": "How this driver affects the trajectory",
        "magnitude": "High/Medium/Low",
        "certainty": "Certain/Likely/Uncertain/Contested",
        "evidence": "Direct quotes or detailed paraphrases with references"
      }
    ],
    "organizational": [],
    "governance": [],
    "societal": [],
    "safety_alignment": [],
    "geopolitical": [],
    "economic": []
  }
}
```

If a category has no drivers, leave it as an empty array `[]`.

---

## DOCUMENT TO ANALYZE:

[full_doc_markdown]
