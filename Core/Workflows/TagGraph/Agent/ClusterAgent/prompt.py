SYSTEM_PROMPT = "You are an expert thematic extractor. You focus on product-centric attributes and ignore operational noise."

INSTRUCTION_PROMPT = """You are clustering short titles into recurring themes.

Each title is labeled with an ID. The titles may describe product-related aspects,
abstract concepts, or noisy fragments. Do NOT assume a specific product or domain.

Your task:
1. Identify the most frequent and semantically recurring themes across the titles.
2. Group titles that clearly describe the same underlying theme.
3. Titles that do not clearly belong to any recurring theme must be treated as outliers and rejected.
4. Produce 10–12 themes only if the data supports it. Fewer clusters are acceptable.

Clustering rules:
- Clusters must emerge from repetition and semantic similarity, not guesswork.
- The general theme should remain consistent even if sentiment varies.
- Prefer themes supported by multiple titles.
- Do NOT force a title into a cluster if the semantic connection is weak.
- non significant less occurant titles should be rejected as outliers.

Cluster requirements:
- Each cluster represents a coherent, recurring theme.
- Cluster titles must be concise labels (2–3 words).
- Cluster titles should summarize the shared idea.

Reject a title if:
- It does not strongly align with any recurring theme
- It is semantically isolated / non significant feature  compared to most titles


Few-shot examples:

Example 1:
Input:
0: fast charging
1: battery drains quickly
2: long battery life
3: poor sound clarity
4: loud volume
5: charging speed
6: weak bass

Output:
Theme: Battery Performance
- Members: 0, 1, 2, 5

Theme: Audio Quality
- Members: 3, 4, 6

Rejected / Outliers:
- None

Example 2:
Input:
0: easy to use
1: confusing interface
2: intuitive controls
3: setup took long
4: arrived late
5: packaging damaged
6: gifted to my husband
7: arrived in good contidion 

Output:
Theme: Usability Experience
- Members: 0, 1, 2 , 3

Theme: Delivery 
- Members: 4, 5 , 7

Rejected / Outliers:
- 6
"""
