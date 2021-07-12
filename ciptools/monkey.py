import sys


def patch():
    eventlet_patch()
    if is_eventlet_patched():
        return True

    gevent_patch()
    if is_gevent_patched():
        return True

    return False


def is_patched():
    return is_eventlet_patched() or is_gevent_patched()


def eventlet_patch():
    # throws an ImportError if eventlet is not installed.
    # this is what we want. then the caller can deal with it.
    # noinspection PyUnresolvedReferences
    import eventlet
    eventlet.monkey_patch()


def gevent_patch():
    # throws an ImportError if gevent is not installed.
    # this is what we want. then the caller can deal with it.
    # noinspection PyUnresolvedReferences
    import gevent.monkey
    gevent.monkey.patch_all()


def is_eventlet_patched():
    if "eventlet.patcher" not in sys.modules:
        return False

    try:
        # noinspection PyUnresolvedReferences
        import eventlet
    except ImportError:
        return False
    else:
        return eventlet.patcher.is_monkey_patched("socket")


def is_gevent_patched():
    if "gevent.monkey" not in sys.modules:
        return False

    try:
        # noinspection PyUnresolvedReferences
        import gevent.monkey
    except ImportError:
        return False
    else:
        return bool(gevent.monkey.saved)
