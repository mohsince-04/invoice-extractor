### Core Concept

A CLI tool that extracts structured JSON data from messy OCR/text receipts using Gemini, then runs **automated math sanity checks in Python** to verify that $\text{Subtotal} + \text{Tax} = \text{Total}$ without blindly trusting LLM output.

![Summary](https://github.com/user-attachments/assets/8189db90-d032-40bf-b46f-4bfea095b0e8 "Note: Ignore vepython, it's just an alias.")

---

### How Each File Works

1. **`src/schemas.py` (Data Schema & Audit Rules)**
* Defines structured models (`LineItem` and `InvoiceData`) using **Pydantic V2**.
* Contains a `@model_validator` that runs Python logic post-extraction to check if item sums and grand totals match mathematically.
* Generates audit notes and sets an `is_math_valid` pass/fail status flag.


2. **`src/extractor.py` (LLM Engine)**
* Sends raw OCR text to `gemini-2.5-flash` via the `google-genai` SDK.
* Enforces structured JSON output using `response_schema=InvoiceData` and a low temperature (`0.1`) for precise extraction.
* Returns a populated `InvoiceData` instance directly via `response.parsed`.


3. **`src/cli.py` (User Interface)**
* CLI built with **Typer** and **Rich**.
* Handles file inputs, shows a loading spinner during API processing, and displays extracted metadata, line-item tables, and a color-coded **Financial Audit Panel** (`PASSED` / `FAILED`).
