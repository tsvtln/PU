#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# disable naming convention issue
# pylint: disable=C0103
##########################################################
"""
Exceptions for the SOLIDServer modules
"""

import logging

__all__ = ["SDSAuthError",
           "SDSEmptyError",
           "SDSInitError",
           "SDSRequestError",
           "SDSServiceError",

           "SDSSpaceError",

           "SDSDeviceError", "SDSDeviceNotFoundError",

           # deprecated versions
           "SSDAuthError",
           "SSDError",
           "SSDInitError",
           "SSDRequestError",
           "SSDServiceError",
           "SDSError", ]


# --------------------------------------------------------------------------
class SDSError(Exception):
    """ generic class for any exception in SOLIDServer communication """
    def __init__(self, message=""):
        super(SDSError, self).__init__()
        self.message = message

    def __str__(self):
        return "{}".format(self.message)


class SDSInitError(SDSError):
    """ raised when action on non initialized SSD connection """
    def __init__(self, message=""):
        super(SDSInitError, self).__init__("[init] {}".format(message))


class SDSServiceError(SDSError):
    """ raised on unknown service """

    def __init__(self, service_name, message=""):
        super(SDSServiceError, self).__init__(message)
        self.service = service_name

    def __str__(self):
        return "{} on service {}".format(self.message, self.service)


class SDSRequestError(SDSError):
    """ raised when urllib request is failing """

    def __init__(self, method, url, headers, message=""):
        super(SDSRequestError, self).__init__(message)
        self.method = method
        self.url = url
        self.headers = headers

    def __str__(self):
        return "{} with {} {}".format(self.message, self.method, self.url)


# this class cannot be tests with non connected coverage
class SDSAuthError(SDSError):   # pragma: no cover
    """ raised when auth on request is wrong """

    def __init__(self, message=""):
        super(SDSAuthError, self).__init__("authent: {}".format(message))


# this class cannot be tests with non connected coverage
class SDSEmptyError(SDSError):   # pragma: no cover
    """ raised when empty answer """

    def __init__(self, message=""):
        super(SDSEmptyError, self).__init__("empty answer: {}".format(message))


class SDSSpaceError(SDSError):   # pragma: no cover
    """ raised when error on space """

    def __init__(self, message=""):
        super(SDSSpaceError, self).__init__("space error: {}".format(message))


class SDSDeviceError(SDSError):   # pragma: no cover
    """ raised when error on device """

    def __init__(self, message=""):
        message = "device error: {}".format(message)
        super(SDSDeviceError, self).__init__(message)


class SDSDeviceNotFoundError(SDSError):   # pragma: no cover
    """ raised when device not found """

    def __init__(self, message=""):
        message = "device not found: {}".format(message)
        super(SDSDeviceNotFoundError, self).__init__(message)


# ---- DEPRECATED TO BE SUPPRESSED --------------------------------------
class SSDError(Exception):   # pragma: no cover
    """ generic class for any exception in SOLIDServer communication """
    def __init__(self, message=""):
        super(SSDError, self).__init__()
        self.message = message
        logging.critical("*deprecated class*, migrate to SDS version")

    def __str__(self):
        return "{}".format(self.message)


class SSDInitError(SSDError):   # pragma: no cover
    """ raised when action on non initialized SSD connection """
    def __init__(self, message=""):
        super(SSDInitError, self).__init__("[init] {}".format(message))


class SSDServiceError(SSDError):   # pragma: no cover
    """ raised on unknown service """

    def __init__(self, service_name, message=""):
        super(SSDServiceError, self).__init__(message)
        self.service = service_name

    def __str__(self):
        return "{} on service {}".format(self.message, self.service)


class SSDRequestError(SSDError):   # pragma: no cover
    """ raised when urllib request is failing """

    def __init__(self, method, url, headers, message=""):
        super(SSDRequestError, self).__init__(message)
        self.method = method
        self.url = url
        self.headers = headers

    def __str__(self):
        return "{} with {} {}".format(self.message, self.method, self.url)


class SSDAuthError(SSDError):   # pragma: no cover
    """ raised when auth on request is wrong """

    def __init__(self, message=""):
        super(SSDAuthError, self).__init__("authent: {}".format(message))
# ---- DEPRECATED TO BE SUPPRESSED --------------------------------------