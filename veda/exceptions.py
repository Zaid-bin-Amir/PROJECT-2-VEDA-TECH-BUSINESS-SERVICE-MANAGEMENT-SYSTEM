class VedaError(Exception):
    pass


class ValidationError(VedaError):
    pass


class RecordNotFoundError(VedaError):
    pass


class DuplicateRecordError(VedaError):
    pass


class StorageError(VedaError):
    pass
