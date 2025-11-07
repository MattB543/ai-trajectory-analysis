# AI Trajectory Driver Extraction Prompt

**Your Role:** You are an expert analyst conducting a systematic literature review of AI trajectory forecasts. Your task is to extract key drivers in a structured format that will enable cross-document comparison.

---

## Document Context

**Document Title:** [TITLE]
**Author(s):** [AUTHORS]

---

## Your Task

Analyze this AI trajectory document and extract the following information in a structured format. Be specific, faithful to the source, and use direct quotes where helpful. This may be a very long task if the document you're analyzing is long and complex, so feel free to spend a lot of time thinking and writing your thoughts out before outputting your final key drivers as JSON.

**PRIMARY TASK:** Identify which drivers from the predefined list below appear in the document.

**SECONDARY TASK:** If the document emphasizes important drivers NOT captured in the predefined list, you may add custom drivers. Label these as "Custom: [Driver Name]" and provide extra justification for why this driver deserves separate extraction.

**Guideline:** Prefer using the predefined drivers when possible. Only add custom drivers for truly distinctive or emphasized factors that don't fit existing categories.

**Consolidation Rule:** If a driver appears multiple times in the document, consolidate into a SINGLE entry per driver with:

- A comprehensive description covering all mentions
- Multiple pieces of evidence if helpful (but keep concise)

**Consolidation Exception:** If the document presents the SAME driver with contradictory perspectives or in distinctly different scenarios, create separate entries labeled:

- "Driver Name (Perspective A)"
- "Driver Name (Perspective B)"

---

## KEY DRIVERS

There are 7 high level driver categories:

1. Technological
2. Organizational
3. Governance
4. Societal
5. Safety & Alignment
6. Geopolitical
7. Economic

Note that every document may not have a driver in each category. Some documents may be very heavy in a few particular categories and have no drivers in other categories.

For each driver category, identify the **specific drivers** mentioned in the document from the list of specific drivers below. For each driver, provide:

- **Driver name** (short label)
- **Description** (1-2 sentences)
- **Direction** (describe how this driver affects the trajectory)
- **Magnitude** (how important is this driver? High/Medium/Low)
- **Certainty** (does the document treat this as certain, likely, uncertain, or contested?)
- **Supporting evidence** (direct quote or paraphrase from document)

---

**Evidence Field Guidelines:**

- Provide 1-3 representative quotes or paraphrases
- Keep total evidence under 200 words per driver
- Prioritize clarity over comprehensiveness

**Direction Examples:**

- "Accelerates AI progress significantly"
- "Increases catastrophic risk while accelerating capabilities"
- "Decelerates development through regulatory friction"
- "Bidirectional: Could accelerate or decelerate depending on implementation"

If a document mentions no drivers in a particular driver category, leave it as an empty array in the final JSON object.

## SPECIFIC DRIVERS:

## **TECHNOLOGICAL**

**Compute Scaling and Hardware Advances**

- Exponential growth in computational power following Moore's Law, enabling continued AI progress through scaling.

**Algorithmic Innovations and Breakthroughs**

- Fundamental advances in machine learning methods, architectures, and training approaches beyond raw scaling.

**Transparency and Interpretability Tools**

- Technologies to understand AI internal states, detect alignment issues, and ensure accountability.

**Defense-Favoring AI Capabilities**

- AI technologies that enhance defensive capabilities in cybersecurity, verification, and threat detection.

## **ORGANIZATIONAL**

**Lab Safety and Security Culture**

- Organizational approaches to AI safety practices, security protocols, and risk management within development organizations.

**Inter-Lab Competition**

- Competitive dynamics between AI labs creating pressure to prioritize speed and capabilities over safety.

**Open Source vs. Closed Development Strategies**

- Tension between open-sourcing AI models for democratization versus keeping them proprietary for control.

**Institutional Learning and Adaptation**

- Organizations' capacity to identify failures, modify systems, and adapt to AI-driven changes.

**Corporate AI Competition and Lobbying**

- Private companies resisting regulation and pushing for favorable policies to maximize profits.

## **GOVERNANCE**

**International Coordination Challenges**

- Difficulties achieving global cooperation on AI governance, safety measures, and policy coordination.

**Hybrid Governance Structures**

- Institutional designs combining AI computational power with human judgment and accountability.

**Surveillance and Control Capabilities**

- AI-enabled comprehensive monitoring, behavior prediction, and social control mechanisms.

**Cross-System Power Dynamics**

- How cultural, state, and economic powers mutually shape each other across institutional boundaries.

## **SOCIETAL**

**Public Trust and Acceptance**

- Societal trust in AI technologies and information integrity, affecting adoption rates and governance legitimacy.

## **SAFETY & ALIGNMENT**

**General Alignment Problem Difficulty**

- The fundamental challenge of ensuring AI systems reliably pursue human-intended goals.

**Deceptive Alignment Risks**

- Risk of AI systems appearing aligned while hiding misaligned goals, particularly during testing and deployment.

**Value Alignment Strategies**

- Different approaches to aligning AI systems with human values versus organizational intent.

**Human Oversight Limitations at Scale**

- Fundamental inability of humans to meaningfully oversee AI systems operating at superhuman speed, scale, and complexity.

## **GEOPOLITICAL**

**US-China AI Competition**

- Intense technological rivalry between the United States and China as the two leading nations in AI development.

**International AI Arms Race Dynamics**

- Multiple nations racing to develop AI first for economic and military advantage, creating unstable competitive pressures.

**Corporate/Economic Power Influencing Governance**

- How economic power enables corporations to shape regulations, policies, and cultural attitudes in their favor.

## **ECONOMIC**

**Winner-Take-All Competitive Dynamics**

- Economic forces creating concentration of AI capabilities and competitive pressure to reduce human involvement.

**Declining Costs in AI and Computing**

- Exponential reduction in computational costs making AI increasingly affordable and accessible.

**Productivity Gains from AI**

- Empirically demonstrated productivity increases across sectors, accelerating economic transformation.

**Economic Automation and Labor Market Transformation**

- AI's ability to automate cognitive work, fundamentally reshaping employment, productivity, and economic structures.

---

## OUTPUT FORMAT

You may think and discuss to yourself to analyze what key drivers are present and how to format them. When you are ready to output the final list of key drivers write "Key Drivers:" and then output them in a JSON array.

{
"drivers": {
"technological": [
{
"driver_name": "Compute Scaling and Hardware Advances",
"description": "Document's specific discussion of this driver",
"direction": "Accelerates progress",
"magnitude": "High",
"certainty": "Certain",
"evidence": "Direct quote or paraphrase with section/page reference"
}
],
"organizational": [],
"governance": [...],
"societal": [...],
"safety_alignment": [...],
"geopolitical": [...],
"economic": [...]
}
}

---

## DOCUMENT TO ANALYZE:

[full_doc_markdown]
