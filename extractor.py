import os

from google import genai
from google.genai import types
from schemas import InvoiceData


def extract_invoice_data(raw_text: str) -> InvoiceData:
    """Extracts structured invoice details from unstructured OCR text using structured outputs."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
    You are an expert financial document parsing system.
    Extract all available invoice/receipt information from the following OCR text.
    Convert currency symbols to standard 3-letter codes where applicable (e.g., $ -> USD, ₹ -> INR).
    Ensure line items, quantities, subtotal, tax, and total amount are accurately extracted.

    RAW OCR TEXT:
    ---
    {raw_text}
    ---
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InvoiceData,
            temperature=0.1,  # Low temperature for deterministic extraction
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

    # The SDK parses directly into the Pydantic schema via response_schema
    invoice: InvoiceData = response.parsed
    return invoice
