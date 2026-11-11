"""Position sizing helpers. These functions do not place trades."""


def calculate_position_size(
    account_balance_nzd: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
) -> dict:
    if account_balance_nzd <= 0:
        raise ValueError("Account balance must be positive.")
    if not 0 < risk_percent <= 1:
        raise ValueError("risk_percent must be a decimal between 0 and 1.")
    if entry_price <= 0 or stop_price <= 0 or stop_price >= entry_price:
        raise ValueError("For a long trade, stop must be positive and below entry.")

    risk_budget = account_balance_nzd * risk_percent
    risk_per_unit = entry_price - stop_price
    quantity = risk_budget / risk_per_unit
    notional = quantity * entry_price

    return {
        "risk_budget_nzd": risk_budget,
        "quantity": quantity,
        "position_value_nzd": notional,
        "risk_percent": risk_percent * 100,
        "note": "Illustrative only; excludes fees, spread, slippage and currency conversion.",
    }
