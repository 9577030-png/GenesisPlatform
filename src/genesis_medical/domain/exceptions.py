class MedicalAIError(Exception):
    """Base exception for the medical domain package."""


class InvalidPatientDataError(MedicalAIError):
    """Invalid patient data."""


class InvalidParameterError(MedicalAIError):
    """Invalid laboratory parameter."""


class ParsingError(MedicalAIError):
    """Invalid medical input format."""


class ConfigurationError(MedicalAIError):
    """Invalid medical configuration or knowledge data."""


class ThresholdNotFoundError(ConfigurationError):
    """Requested threshold is not available."""


class GuidelineLoadError(ConfigurationError):
    """Clinical guideline could not be loaded."""


class InferenceError(MedicalAIError):
    """Medical inference failed."""


class ConflictResolutionError(MedicalAIError):
    """Medical conflict resolution failed."""
