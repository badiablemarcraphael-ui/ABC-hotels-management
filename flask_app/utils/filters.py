def float_filter(value):
    """Convert value to float"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0