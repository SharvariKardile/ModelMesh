def analyze_query(query: str):
    """
    Analyze the complexity of a user query
    using multiple heuristic signals.
    """

    query_lower = query.lower()
    words = query_lower.split()
    word_count = len(words)

    # -----------------------------
    # 1. Base score from query length
    # -----------------------------

    if word_count <= 5:
        score = 0.2

    elif word_count <= 15:
        score = 0.4

    elif word_count <= 30:
        score = 0.6

    else:
        score = 0.75

    signals = []

    # -----------------------------
    # 2. Reasoning signals
    # -----------------------------

    reasoning_keywords = [
        "explain",
        "analyze",
        "compare",
        "evaluate",
        "why",
        "reason",
        "justify",
        "design"
    ]

    if any(keyword in query_lower for keyword in reasoning_keywords):
        score += 0.10
        signals.append("reasoning")

    # -----------------------------
    # 3. Technical signals
    # -----------------------------

    technical_keywords = [
        "code",
        "algorithm",
        "database",
        "api",
        "architecture",
        "machine learning",
        "deep learning",
        "distributed",
        "system",
        "network",
        "security"
    ]

    if any(keyword in query_lower for keyword in technical_keywords):
        score += 0.10
        signals.append("technical")

    # -----------------------------
    # 4. Multi-step signals
    # -----------------------------

    multi_step_keywords = [
        "step by step",
        "steps",
        "first",
        "then",
        "finally",
        "and explain",
        "and implement"
    ]

    if any(keyword in query_lower for keyword in multi_step_keywords):
        score += 0.10
        signals.append("multi_step")

    # -----------------------------
    # 5. Multiple requirements
    # -----------------------------

    requirement_words = [
        "and",
        "also",
        "including",
        "requirements",
        "features",
        "cover",
        "consider"
    ]

    requirement_count = sum(
        1 for word in requirement_words
        if word in words
    )

    comma_count = query.count(",")

    if requirement_count >= 2 or comma_count >= 2:
        score += 0.10
        signals.append("multiple_requirements")

    # -----------------------------
    # 6. Keep score between 0 and 1
    # -----------------------------

    score = min(score, 1.0)

    # -----------------------------
    # 7. Convert score to complexity
    # -----------------------------

    if score < 0.40:
        complexity = "low"

    elif score < 0.70:
        complexity = "medium"

    else:
        complexity = "high"

    # -----------------------------
    # 8. Return analysis result
    # -----------------------------

    return {
        "complexity": complexity,
        "score": round(score, 2),
        "signals": signals
    }