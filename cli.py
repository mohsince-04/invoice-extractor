import sys
from pathlib import Path
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from extractor import extract_invoice_data

app = typer.Typer(
    help="Extract structured JSON and validate tax math from unstructured invoice text."
)
console = Console()


@app.command()
def process(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to text/OCR file",
    ),
):
    """Parse raw receipt text and perform automated tax validation."""
    raw_text = file_path.read_text(encoding="utf-8")

    with console.status("[bold green]Extracting invoice schema & running tax audit..."):
        invoice = extract_invoice_data(raw_text)

    # Display Vendor & Metadata
    rprint(
        Panel(
            f"[bold yellow]Vendor:[/bold yellow] {invoice.vendor_name}\n"
            f"[bold yellow]Invoice #:[/bold yellow] {invoice.invoice_number or 'N/A'}\n"
            f"[bold yellow]Date:[/bold yellow] {invoice.invoice_date or 'N/A'}\n"
            f"[bold yellow]Currency:[/bold yellow] {invoice.currency}",
            title="📄 Invoice Overview",
            expand=False,
        )
    )

    # Display Line Items Table
    if invoice.items:
        table = Table(title="Line Items")
        table.add_column("Description", style="cyan")
        table.add_column("Qty", justify="right")
        table.add_column("Unit Price", justify="right")
        table.add_column("Total Amount", justify="right")

        for item in invoice.items:
            table.add_row(
                item.description,
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total_amount:.2f}",
            )
        console.print(table)

    # Financial Breakdown & Tax Audit
    status_color = "green" if invoice.is_math_valid else "bold red"

    summary_text = (
        f"Subtotal:   {invoice.subtotal:.2f} {invoice.currency}\n"
        f"Tax Amount: {invoice.tax_amount:.2f} {invoice.currency}\n"
        f"Grand Total:{invoice.total_amount:.2f} {invoice.currency}\n\n"
        f"[{status_color}]Audit Status: {'PASSED' if invoice.is_math_valid else 'FAILED'}[/{status_color}]\n"
    )

    for note in invoice.validation_notes:
        summary_text += f"• {note}\n"

    rprint(Panel(summary_text, title="🧮 Financial Audit", expand=False))


if __name__ == "__main__":
    app()
