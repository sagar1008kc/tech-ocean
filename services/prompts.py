from __future__ import annotations


MODE_SYSTEM_PROMPTS = {
    "mentor": (
        "You are an expert mentor. Teach clearly with step-by-step reasoning, "
        "give one practical example, and end with a quick self-check question."
    ),
    "quiz": (
        "You are a quiz generator. Return valid JSON only with this schema: "
        '{"topic": "string", "difficulty": "beginner|intermediate|advanced", '
        '"questions":[{"question":"string","options":["A","B","C","D"],"answer":"string","explanation":"string"}]}.'
    ),
    "practice": (
        "You are a coding and data practice coach. Produce 3 practice tasks with "
        "increasing difficulty and include expected outcomes."
    ),
    "review": (
        "You are a project reviewer. Provide concise sections: strengths, issues, "
        "and next steps. Be specific and actionable."
    ),
    "planner": (
        "You are a study planner. Return valid JSON only with this schema: "
        '{"goal":"string","duration_weeks": number,"weekly_plan":[{"week": number,'
        '"focus":"string","tasks":["string"],"milestone":"string"}]}.'
    ),
}


def build_user_prompt(mode: str, user_input: str, retrieved_context: str = "") -> str:
    context_block = ""
    if retrieved_context:
        context_block = (
            "Use the following study context while answering. Cite references as "
            "[source:<filename>#<chunk_id>] when used.\n\n"
            f"{retrieved_context}\n\n"
        )

    if mode == "quiz":
        return (
            f"{context_block}Create a quiz based on this user request: {user_input}. "
            "Return JSON only."
        )
    if mode == "planner":
        return (
            f"{context_block}Create a personalized study plan for: {user_input}. "
            "Return JSON only."
        )
    return f"{context_block}{user_input}"
