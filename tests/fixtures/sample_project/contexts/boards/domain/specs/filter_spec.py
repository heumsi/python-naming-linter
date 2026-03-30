class ValidationError(Exception):
    pass


class FilterError(ValidationError):  # violation: not {Subject}{Condition}Error
    pass


class FilterNotFoundError(ValidationError):  # pass
    pass
