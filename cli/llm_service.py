# cli/llm_service.py
import ollama
from ollama import ResponseError
from requests.exceptions import ConnectionError
from rich.console import Console

# Import the templates from their dedicated file
from .prompts import GENERATE_PROMPT_TEMPLATE, REVIEW_PROMPT_TEMPLATE, IMAGE_PROMPT_TEMPLATE ,IMAGE_TEXT_PROMPT_TEMPLATE ,STRUCTURED_IMAGE_DATA_PROMPT_TEMPLATE


class LLMService:
    """
    A service class to manage all interactions with the Ollama LLM.
    """
    def __init__(self, model_name: str):
        """
        Initializes the LLMService.

        Args:
            model_name (str): The default Ollama model to use (e.g., 'stable-code:3b').
        """
        self.model = model_name
        self.console = Console()

    def _invoke_llm(self, prompt: str, model: str, images: list[str] | None = None) -> str:
        """
        Private method to send a prompt to the Ollama model and handle errors.
        Can handle both text-only and multimodal requests.

        Args:
            prompt (str): The complete prompt to send to the LLM.
            model (str): The name of the model to use for this specific call.
            images (list[str] | None): A list of paths to images for multimodal models.

        Returns:
            str: The raw response text from the LLM.
        
        Raises:
            SystemExit: If a connection to Ollama fails or the model causes an error.
        """
        try:
            response = ollama.generate(model=self.model, prompt=prompt, stream=False)
            return response.get('response', '')
        except ConnectionError:
            self.console.print("\n[bold red]Connection Error:[/bold red] Could not connect to Ollama.")
            self.console.print("Please make sure the Ollama application or server is running.")
            raise SystemExit(1)
        except ResponseError as e:
            self.console.print(f"\n[bold red]Ollama API Error:[/bold red] {e.error}")
            self.console.print(f"This might mean the model '{self.model}' is not available. Please pull it with 'ollama pull {self.model}'.")
            raise SystemExit(1)
        except Exception as e:
            self.console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")
            raise SystemExit(1)

    def _clean_code_output(self, response_text: str) -> str:
        """
        Cleans the LLM's response to extract only the code from a markdown block.
        This is a pragmatic approach for models that tend to wrap code in ```.

        Args:
            response_text (str): The raw response from the LLM.

        Returns:
            str: The cleaned, code-only string.
        """
        # Find the first ``` which marks the start of the code block
        code_start = response_text.find("```")
        if code_start != -1:
            # Find the next ``` which marks the end
            code_end = response_text.find("```", code_start + 3)
            if code_end != -1:
                # Extract the content between the fences
                content = response_text[code_start + 3:code_end].strip()
                # Remove the language specifier if present (e.g., "python\n")
                first_line_end = content.find('\n')
                if first_line_end != -1 and not content[:first_line_end].strip().isspace() and len(content[:first_line_end].strip()) < 15:
                    content = content[first_line_end + 1:]
                return content.strip()

        # If no markdown fences are found, return the entire response, stripped.
        return response_text.strip()

    def generate_code(self, user_prompt: str, context: str) -> str:
        """
        Generates code based on a user prompt and context from the 'practices' database.

        Args:
            user_prompt (str): The user's request for code generation.
            context (str): Relevant code snippets and best practices.

        Returns:
            str: The generated code, cleaned and ready to use.
        """
        full_prompt = GENERATE_PROMPT_TEMPLATE.format(
            context=context or "No context provided.",
            user_prompt=user_prompt
        )
        raw_response = self._invoke_llm(full_prompt)
        return self._clean_code_output(raw_response)

    def generate_code_from_structured_data(self, user_prompt: str, structured_data: str) -> str:
        """
        Generates code based on a text prompt and structured data from an image.

        Args:
            user_prompt (str): The user's text request accompanying the image.
            structured_data (str): The key-value data extracted by the vOCR service.

        Returns:
            str: The generated code, cleaned and ready to use.
        """
        full_prompt = STRUCTURED_IMAGE_DATA_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt,
            structured_data=structured_data
        )
        raw_response = self._invoke_llm(full_prompt)
        return self._clean_code_output(raw_response)

    # # NEW method for the pipeline
    # def generate_code_from_image_text(self, user_prompt: str, image_text: str) -> str:
    #     """
    #     Generates code based on a text prompt and text extracted from an image.

    #     Args:
    #         user_prompt (str): The user's text request accompanying the image.
    #         image_text (str): The text extracted by the OCR service.

    #     Returns:
    #         str: The generated code, cleaned and ready to use.
    #     """
    #     full_prompt = IMAGE_TEXT_PROMPT_TEMPLATE.format(
    #         user_prompt=user_prompt,
    #         image_text=image_text
    #     )
    #     raw_response = self._invoke_llm(full_prompt)
    #     return self._clean_code_output(raw_response)

    def generate_review(self, code_to_review: str, context: str) -> str:
        # ... same as before ...
        full_prompt = REVIEW_PROMPT_TEMPLATE.format(
            context=context or "No bad practice examples provided.",
            code_to_review=code_to_review
        )
        review_text = self._invoke_llm(full_prompt)
        return review_text.strip()