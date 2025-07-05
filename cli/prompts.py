# cli/prompts.py
"""
This module contains the prompt templates used for interacting with the LLM.
Separating them here makes the main service logic cleaner and the prompts easier to edit.
"""

GENERATE_PROMPT_TEMPLATE = """
You are an expert programmer. Your task is to write clean, efficient code to fulfill the user's request.
Use the provided context of best practices and examples from the user's codebase to guide your response.
Generate ONLY the code requested. Do not include any explanations, conversation, or markdown fences (```).

--- CONTEXT (BEST PRACTICES & EXAMPLES) ---
{context}
--- END CONTEXT ---

USER REQUEST: {user_prompt}

CODE:
"""

REVIEW_PROMPT_TEMPLATE = """
You are a world-class code reviewer. Your task is to analyze the user's code and provide constructive feedback.
Your goal is to help the user improve their code by identifying potential bugs, style issues, anti-patterns, and areas for improvement.
Use the provided context, which contains examples of BAD PRACTICES, to help identify similar issues in the user's code.
Be specific and suggest concrete improvements. Format your output as a markdown-formatted review.

--- CONTEXT (EXAMPLES OF BAD PRACTICES TO LOOK FOR) ---
{context}
--- END CONTEXT ---

USER'S CODE TO REVIEW:
{code_to_review}
YOUR REVIEW:
"""