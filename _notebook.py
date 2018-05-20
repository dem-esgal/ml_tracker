# -*- coding: utf-8 -*-

import sys

NOTEBOOK_MAPPING = {}

try:
    import notebook
    import IPython
    from notebook.utils import url_path_join
    from notebook.base.handlers import IPythonHandler
    from IPython.core.magics.namespace import NamespaceMagics
    from IPython import get_ipython

    from ._real_notebook import (
        _jupyter_server_extension_paths,
        _jupyter_nbextension_paths,
        load_jupyter_server_extension,
        get_notebook_id,
    )

    HAS_NOTEBOOK = True

except ImportError:

    from ._not_notebook import (
        _jupyter_server_extension_paths,
        _jupyter_nbextension_paths,
        load_jupyter_server_extension,
        get_notebook_id,
    )

    HAS_NOTEBOOK = False


def in_notebook_environment():
    return "ipykernel" in sys.modules
