# src/transaction_ai/categorization.py
from vertexai.language_models import TextGenerationModel  # For Gemini-Pro

from src.utils.gcp_auth import init_vertex_ai_sdk
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Vertex AI SDK
init_vertex_ai_sdk()


def get_gemini_model():
    """Gets the Gemini-Pro model for text generation."""
    try:
        return TextGenerationModel.from_pretrained("gemini-pro")
    except Exception as e:
        logger.error(f"Error loading Gemini-Pro model: {e}")
        raise


def suggest_category_with_gemini(
    transaction_description: str, existing_categories: list
) -> str:
    """
    Suggests an accounting category for a transaction using Gemini-Pro.

    Args:
        transaction_description (str): The description of the financial transaction.
        existing_categories (list): A list of valid accounting categories (e.g., ["Rent", "Utilities", "Salaries", "Office Supplies", "Travel Expenses"]).

    Returns:
        str: The suggested category or "Uncategorized" if not confident.
    """
    model = get_gemini_model()

    prompt = f"""
    You are an intelligent accounting assistant. Given a transaction description, categorize it into one of the following predefined categories. If none fit well, suggest 'Other' or 'Uncategorized'.

    Available Categories: {', '.join(existing_categories)}.

    Transaction Description: "{transaction_description}"

    Suggested Category:
    """

    try:
        response = model.predict(prompt=prompt, temperature=0.2, max_output_tokens=50)
        suggested_category = response.text.strip()
        # Basic validation: ensure the suggested category is one of the allowed ones, or a fallback
        if suggested_category in existing_categories or suggested_category in [
            "Other",
            "Uncategorized",
        ]:
            logger.info(
                f"Categorized '{transaction_description}' as: {suggested_category}"
            )
            return suggested_category
        else:
            logger.warning(
                f"Gemini suggested an unrecognized category '{suggested_category}' for '{transaction_description}'. Defaulting to 'Uncategorized'."
            )
            return "Uncategorized"
    except Exception as e:
        logger.error(f"Error calling Gemini for categorization: {e}")
        return "Categorization_Error"


# For a custom endpoint, you would import and use get_aiplatform_endpoint_client
# and the appropriate prediction instance schema.
