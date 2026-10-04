def final_price(qty, unit_price, bulk_threshold, bulk_discount):
    """Total price with bulk discount. BUG: discount never applied."""
    return qty * unit_price
