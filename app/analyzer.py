def analyze_query(query: str):
    """
    Analyze the complexity of a user query.
    """

    word_count = len(query.split())

    if word_count <= 5:
        complexity = "low"
        score = 0.2

    elif word_count <= 15:
        complexity = "medium"
        score = 0.5

    else:
        complexity = "high"
        score = 0.8

    return {
        "complexity": complexity,
        "score": score
    }