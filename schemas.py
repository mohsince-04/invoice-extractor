from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class LineItem(BaseModel):
    description: str = Field(description="Description of the product or service")
    quantity: float = Field(default=1.0, ge=0, description="Quantity of items")
    unit_price: float = Field(ge=0, description="Price per single unit")
    total_amount: float = Field(ge=0, description="Total amount for this line item")


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = Field(
        default=None, description="Unique invoice ID or reference number"
    )
    vendor_name: str = Field(description="Name of the merchant or issuing company")
    invoice_date: Optional[str] = Field(
        default=None, description="Date of issuance (YYYY-MM-DD if possible)"
    )
    currency: str = Field(
        default="USD", description="3-letter ISO currency code or symbol"
    )
    items: List[LineItem] = Field(
        default_factory=list, description="List of itemized goods or services"
    )
    subtotal: float = Field(ge=0, description="Sum of line items before tax")
    tax_amount: float = Field(default=0.0, ge=0, description="Total tax applied")
    round_off: float = Field(
        default=0.0,
        description="Optional round-off adjustment or discount (can be positive or negative)",
    )
    total_amount: float = Field(ge=0, description="Final grand total")

    # Validation status generated during post-processing
    is_math_valid: bool = Field(
        default=True,
        description="True if subtotal + tax + round_off equals total_amount within rounding tolerance",
    )
    validation_notes: List[str] = Field(
        default_factory=list,
        description="Automated audit notes regarding tax/math sanity checks",
    )

    @model_validator(mode="after")
    def validate_invoice_math(self) -> "InvoiceData":
        """Automated tax, round-off, and subtotal sanity check."""
        calculated_subtotal = sum(item.total_amount for item in self.items)

        # Factor in round_off adjustment
        expected_total = round(self.subtotal + self.tax_amount + self.round_off, 2)
        actual_total = round(self.total_amount, 2)

        # 1. Check line items sum vs reported subtotal
        if self.items and abs(calculated_subtotal - self.subtotal) > 0.05:
            self.validation_notes.append(
                f"Warning: Sum of line items ({calculated_subtotal:.2f}) does not match reported subtotal ({self.subtotal:.2f})."
            )

        # 2. Audit note for round-off presence
        if abs(self.round_off) > 0.001:
            self.validation_notes.append(
                f"Round-off adjustment applied: {self.round_off:+.2f} {self.currency}."
            )

        # 3. Check grand total math
        if abs(expected_total - actual_total) > 0.05:
            self.is_math_valid = False
            self.validation_notes.append(
                f"Math Mismatch: Subtotal ({self.subtotal:.2f}) + Tax ({self.tax_amount:.2f}) + Round Off ({self.round_off:.2f}) = {expected_total:.2f}, but reported total is {actual_total:.2f}."
            )
        else:
            self.validation_notes.append(
                "Tax, round-off, and total math verified successfully."
            )

        return self
