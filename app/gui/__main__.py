"""支援 python -m app.gui 直接執行"""

# Pre-warm numpy BEFORE any PySide6 import.
# PySide6/shiboken runs update_mapping() when the first widget is created;
# that routine iterates sys.modules and attempts to import any C extension
# it finds.  If pandas/sklearn are *partially* initialised at that point
# (loaded as a side-effect of torch inside a worker thread), the mapping
# update triggers a circular import and the process dies with:
#   AttributeError: partially initialized module 'pandas' has no
#     attribute '_pandas_datetime_CAPI'
# Importing numpy here ensures the fundamental numeric C extensions are
# fully registered before shiboken ever touches them.
try:
    import numpy as _np  # noqa: F401
except ImportError:
    pass

from app.gui.app import main  # noqa: E402

if __name__ == "__main__":
    main()
