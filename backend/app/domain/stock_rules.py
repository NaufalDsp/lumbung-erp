from app.domain.exceptions import StockInsufficientError, StockInvariantViolationError


def validate_stock_invariants(on_hand: int, reserved: int) -> None:
    """Enforces non-negotiable database & domain invariants for inventory:

    1. on_hand >= 0
    2. reserved >= 0
    3. reserved <= on_hand
    """
    if on_hand < 0:
        raise StockInvariantViolationError(
            f"Stok fisik (on_hand) tidak boleh negatif: {on_hand}")
    if reserved < 0:
        raise StockInvariantViolationError(
            f"Stok reservasi (reserved) tidak boleh negatif: {reserved}")
    if reserved > on_hand:
        raise StockInvariantViolationError(
            f"Stok reservasi ({reserved}) tidak boleh melebihi stok fisik ({on_hand})"
        )


def calculate_available_stock(on_hand: int, reserved: int) -> int:
    """Calculates available stock = on_hand - reserved.

    Validates invariants first.
    """
    validate_stock_invariants(on_hand, reserved)
    return on_hand - reserved


def ensure_sufficient_stock(product_id: int, on_hand: int, reserved: int, requested: int) -> None:
    """Ensures available stock is sufficient for requested reservation or fulfillment."""
    available = calculate_available_stock(on_hand, reserved)
    if available < requested:
        raise StockInsufficientError(
            product_id=product_id,
            available=available,
            requested=requested,
        )


def calculate_moving_average_cost(
    old_qty: int,
    old_avg_cost: int,
    received_qty: int,
    unit_cost: int,
) -> int:
    """Calculates new weighted moving average unit cost when goods are received.

    Formula (PRD 7.5):
    biaya_rata2_baru = (nilai_lama + nilai_masuk) / (qty_lama + qty_masuk),
    rounded half-up to nearest integer Rupiah.
    """
    if received_qty <= 0:
        return old_avg_cost

    total_qty = old_qty + received_qty
    if total_qty <= 0:
        return 0

    total_value = (old_qty * old_avg_cost) + (received_qty * unit_cost)

    # Half-up rounding for integer division: (numerator + denominator // 2) // denominator
    new_avg_cost = (total_value + (total_qty // 2)) // total_qty
    return max(0, new_avg_cost)
