# cli/image_service.py
from jigsawstack import JigsawStack
from rich.console import Console

class ImageService:
    """
    A service class to manage image-to-text extraction using JigsawStack.
    """
    def __init__(self, api_key: str):
        if not api_key or "YOUR_JIGSAW_API_KEY" in api_key:
            raise ValueError("JigsawStack API key is not configured. Please set it in main.py.")
        # The correct client initialization is just this:
        self.client = JigsawStack(api_key=api_key)
        self.console = Console()

    def extract_structured_data_from_image(self, image_path: str, extraction_prompts: list[str]) -> str | None:
        """
        Extracts structured data from an image using the JigsawStack Vision vOCR endpoint.

        Args:
            image_path (str): The path to the local image file.
            extraction_prompts (list[str]): A list of labels for the data to extract.

        Returns:
            str | None: A formatted string of key-value pairs, or None on failure.
        """
        try:
            self.console.print(f"[yellow]🔍 Querying image for: {', '.join(extraction_prompts)}...[/yellow]")
            with open(image_path, "rb") as f:
                # Use the correct vision.vocr endpoint
                # NEW - CORRECT CODE
                response = self.client.vision.vocr(image=f, prompt=extraction_prompts)

            if response and response.output:
                # Format the dictionary output into a clean string for the LLM
                formatted_output = "\n".join([f"{key}: {value}" for key, value in response.output.items()])
                return formatted_output
            else:
                self.console.print("[bold red]API Error:[/bold red] The service did not return any structured data.")
                return None
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred with the Image Service: {e}[/bold red]")
            return None 