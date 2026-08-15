class MLPlatformError(Exception):
    """Base domain exception."""


class DataValidationError(MLPlatformError):
    """Dataset violates a critical contract."""


class ModelUnavailableError(MLPlatformError):
    """No verified production model can be loaded."""


class FeatureStoreUnavailableError(MLPlatformError):
    """Feature store dependency is unavailable."""
