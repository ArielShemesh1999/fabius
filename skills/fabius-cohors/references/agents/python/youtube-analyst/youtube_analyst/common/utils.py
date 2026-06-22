import os


def load_prompt(base_dir: str, filename: str) -> str:
    """
    Loads a prompt text from a file.

    Args:
        base_dir: The directory containing the 'prompts' subdirectory.
                  Typically passed as os.path.dirname(__file__) from the calling agent.
        filename: The name of the prompt file (e.g., 'agent_prompt.txt').

    Returns:
        The content of the prompt file.
    """
    prompt_path = os.path.join(base_dir, "prompts", filename)
    with open(prompt_path) as f:
        return f.read()
