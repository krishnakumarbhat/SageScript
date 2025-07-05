def clean_llm_output(response_text: str) -> str:
    """Cleans the LLM output to extract only the code block."""
    # Find the start of a markdown code block
    code_start = response_text.find("```")
    if code_start != -1:
        # Find the end of the block
        code_end = response_text.rfind("```")
        if code_end > code_start:
            # Extract content between the fences
            content = response_text[code_start + 3:code_end].strip()
            # Remove the optional language identifier (e.g., 'python')
            if content.startswith(('python', 'javascript', 'typescript', 'go')):
                content = content[content.find('\n') + 1:]
            return content.strip()
    # If no markdown block is found, return the raw text stripped of whitespace
    return response_text.strip()

def create_llm_prompt(query: str, context: str) -> str:
    """Creates a structured prompt for the LLM."""
    return f"""
You are an expert programmer and a world-class coding assistant.
Your task is to answer the user's query based on the provided code context.
The context contains relevant code snippets from the user's local codebase.
Generate only the code required to fulfill the request. Do not add any conversational text, explanations, or markdown fences.

--- CONTEXT ---
{context}
```

--- END CONTEXT ---

USER QUERY: {query}

CODE:
"""
