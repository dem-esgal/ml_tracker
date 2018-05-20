# -*- coding: utf-8 -*-

import copy
import errno
import hashlib
import json
import logging
from os.path import abspath

from IPython import get_ipython

LOGGER = logging.getLogger(__name__)
NOTEBOOK_MAPPING = {}


def _jupyter_server_extension_paths():
    return [{"module": "ml_tracker"}]


def _jupyter_nbextension_paths():
    return []


def load_jupyter_server_extension(nbapp):
    nbapp.log.info("ML Tracker extension activated!")

    contents_manager = nbapp.contents_manager
    contents_manager.pre_save_hook = pre_save_hook


def get_notebook_id():
    _Jupyter = get_ipython()
    print(_Jupyter)
    if _Jupyter is None:
        return None

    try:
        return _Jupyter.kernel.shell.user_ns["NOTEBOOK_ID"]

    except KeyError:
        return None


def get_hash_content(model):
    json_model = json.dumps(model, sort_keys=True)
    content_hash = hashlib.sha1(json_model.encode("utf-8")).hexdigest()

    return content_hash, json_model

def parse_jupyter_server_model(model):
    for cell in model["content"]["cells"]:
        if cell["cell_type"] != "code":
            continue

        cell["execution_count"] = None

        for output in cell["outputs"]:
            output["execution_count"] = None

    return model


def pre_save_hook(model, **kwargs):
    local_path = kwargs.pop("path", None)

    if local_path is None:
        LOGGER.warning("No notebook path given, cannot save it")
        return

    path = abspath(local_path)

    if model["type"] != "notebook":
        return

    # only for nbformat v4
    if model["content"]["nbformat"] != 4:
        return

    new_model = parse_jupyter_server_model(copy.deepcopy(model))

    content_hash, json_model = get_hash_content(new_model)

    NOTEBOOK_MAPPING[path] = content_hash
