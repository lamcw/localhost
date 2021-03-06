class SessionExpiredError(Exception):
    """Raise when bidding session has expired."""
    pass


class ItemUnavailableError(Exception):
    """Raise when property item is no longer available."""
    pass


class WalletOperationError(ValueError):
    """Raise when wallet operation is invalid."""
    pass


class BidAmountError(ValueError):
    """Raise when bid amount is invalid."""
    pass


class BidBuyoutError(ValueError):
    """Raise when bid amount is greater than buyout price"""
    pass
