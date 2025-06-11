# src/transaction_ai/reconciliation.py
from src.utils.logger import get_logger

logger = get_logger(__name__)


def reconcile_transactions(bank_transactions: list, gl_transactions: list) -> dict:
    """
    Placeholder for reconciliation logic.
    This function would compare transactions from bank statements (parsed by Document AI)
    with general ledger entries, identify matches, and flag discrepancies.
    Gemini could be used here to suggest reasons for mismatches or improve matching logic.
    """
    logger.info("Reconciliation logic will be implemented here.")
    # Example: Simple matching by amount and date
    matches = []
    unmatched_bank = []
    unmatched_gl = []

    # In a real scenario, use more sophisticated algorithms (e.g., fuzzy matching,
    # embedding similarity with Gemini, rule-based systems)
    # For now, just a basic loop to show intent
    for bt in bank_transactions:
        found_match = False
        for glt in gl_transactions:
            if bt.get("amount") == glt.get("amount") and bt.get("date") == glt.get(
                "date"
            ):
                matches.append({"bank_tx": bt, "gl_tx": glt})
                found_match = True
                break
        if not found_match:
            unmatched_bank.append(bt)

    # Add unmatched GL transactions (simplified, in real world needs to handle already matched GLT)
    for glt in gl_transactions:
        is_matched = False
        for match in matches:
            if glt == match["gl_tx"]:
                is_matched = True
                break
        if not is_matched:
            unmatched_gl.append(glt)

    return {
        "matches": matches,
        "unmatched_bank": unmatched_bank,
        "unmatched_gl": unmatched_gl,
    }
