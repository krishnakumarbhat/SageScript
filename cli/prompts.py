# cli/prompts.py

# Prompt for generating code from a text description and context examples.
GENERATE_PROMPT_TEMPLATE = """
You are an expert programmer. Your goal is to write clean, efficient, and correct code based on the user's request.
Use the following best practice examples as context and inspiration.

--- CONTEXT (Good Code Examples) ---
{context}
--- END OF CONTEXT ---

Based on the context and the user's request, generate the code.
Respond ONLY with the code inside a single markdown block. Do not add any explanation, preamble, or conclusion.

User Request: {user_prompt}
"""

# Prompt for reviewing user-submitted code against bad practice examples.
REVIEW_PROMPT_TEMPLATE = """
You are a senior code reviewer. Your task is to analyze the user's code and identify potential issues, suggesting improvements.
Use the following 'bad practice' examples as context for what to look for. These examples show common mistakes or anti-patterns.

--- CONTEXT (Bad Practice Examples to look for) ---
{context}
--- END OF CONTEXT ---

Review the following code submitted by the user.
Provide a constructive, markdown-formatted review. Identify issues, explain why they are problematic, and suggest specific code changes for improvement.
If the code is good, acknowledge it.

--- CODE TO REVIEW ---
{code_to_review}
--- END OF REVIEW ---
"""

# NEW: Prompt for generating code from an image.
IMAGE_PROMPT_TEMPLATE = """
You are an expert programmer specializing in turning software architecture diagrams into code.
Analyze the attached image, which could be a flowchart, UML diagram, wireframe, or whiteboard sketch.

Based on the visual information in the image and the user's request below, write a complete and functional code implementation.
The code should accurately reflect the logic, components, and relationships shown in the diagram.
Respond ONLY with the code inside a single markdown block.

User Request: {user_prompt}
"""


IMAGE_TEXT_PROMPT_TEMPLATE = """
You are an expert programmer. The user has provided text that was automatically extracted from an image using an OCR tool.
This text might represent code, a diagram's labels, or a user interface. It may be unstructured or have OCR errors.
Your task is to interpret this text, understand the user's intent, and write a complete and functional code implementation.

--- TEXT EXTRACTED FROM IMAGE ---
{image_text}
--- END OF EXTRACTED TEXT ---

Based on the extracted text and the user's request, generate the code.
Respond ONLY with the code inside a single markdown block. Do not add any explanation.

User Request: {user_prompt}
"""


STRUCTURED_IMAGE_DATA_PROMPT_TEMPLATE = """
You are an expert programmer. The user has provided structured key-value data that was extracted from an image.
This data represents elements like form fields, button labels, titles, or schema definitions.
Your task is to interpret this structured data and write a complete and functional code implementation based on the user's request.

--- STRUCTURED DATA EXTRACTED FROM IMAGE ---
{structured_data}
--- END OF EXTRACTED DATA ---

Based on the structured data and the user's request below, generate the code.
Respond ONLY with the code inside a single markdown block. Do not add any explanation.

User Request: {user_prompt}
"""