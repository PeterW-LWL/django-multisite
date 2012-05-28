# -*- coding: utf-8 -*

from warnings import warn

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


def get_request():
    return getattr(_thread_locals, 'request', None)


class ThreadLocalsMiddleware(object):
    """Middleware that saves request in thread local starage"""
    def process_request(self, request):
        _thread_locals.request = request


class SiteID(local):
    """
    Dynamic settings.SITE_ID replacement, which acts like an integer.

    django.contrib.sites can allow multiple Django sites to share the
    same database. However, they cannot share the same code by
    default.

    SiteID can be used to replace the static settings.SITE_ID integer
    when combined with the appropriate middleware.
    """

    def __init__(self, default=None, *args, **kwargs):
        """
        ``default``, if specified, determines the default SITE_ID,
        if it is unset.
        """
        if default is not None and not isinstance(default, (int, long)):
            raise ValueError("%r is not a valid default." % default)
        self.default = default
        self.reset()

    def __repr__(self):
        return str(self.__int__())

    def __int__(self):
        if self.site_id is None:
            if self.default is None:
                raise ValueError('SITE_ID has not been set.')
            return self.default
        return self.site_id

    def __lt__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() < other
        elif isinstance(other, SiteID):
            return self.__int__() < other.__int__()
        return True

    def __le__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() <= other
        elif isinstance(other, SiteID):
            return self.__int__() <= other.__int__()
        return True

    def __eq__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() == other
        elif isinstance(other, SiteID):
            return self.__int__() == other.__int__()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __hash__(self):
        return self.__int__()

    def set(self, value):
        from django.db.models import Model
        if isinstance(value, Model):
            value = value.pk
        self.site_id = value

    def reset(self):
        self.site_id = None


def SiteIDHook():
    """Deprecated: Use multisite.SiteID(default=1) for identical behaviour."""
    warn('Use multisite.SiteID instead of multisite.threadlocals.SiteIDHook',
         DeprecationWarning, stacklevel=2)
    return SiteID(default=1)
