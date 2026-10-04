def final_price(qty, unit_price, bulk_threshold, bulk_discount):
    """Total price; bulk discount applies when qty >= bulk_threshold."""
    if qty >= bulk_threshold:
        return qty * unit_price * bulk_discount
    return qty * unit_price
