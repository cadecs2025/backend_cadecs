from rest_framework.exceptions import APIException


class ValidationError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class Warning(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class AuthenticationError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class InvalidTokenError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class TokenDecodError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class NotFound(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class ValueMatchError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class ResponseError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class PageNotFound(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail


class AuthorizationError(APIException):
    def __init__(self, error="", detail=""):
        self.error = error
        self.detail = detail

