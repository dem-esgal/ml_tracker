# -*- coding: utf-8 -*-

import atexit
from datetime import datetime
import inspect
import json
import logging
import os
import os.path
import sys
import traceback
import uuid

from .report import Report

LOGGER = logging.getLogger(__name__)

from ._notebook import (
    _jupyter_server_extension_paths,
    _jupyter_nbextension_paths,
    load_jupyter_server_extension,
    get_notebook_id,
    in_notebook_environment,
)


def generate_guid():
    """
    Generate a GUID
    """
    return str(uuid.uuid4()).replace("-", "")


class Experiment(object):
    def __init__(
            self,
            name=None,
            version=None,
            log_code=False
    ):
        """
        Creates a new experiment.
        Args:
            name: Default(None) - name of experiment
            version: Default(None) - version of experiment
        """

        self.code = ""
        self.attachments = []
        self.context = None
        self.commited = False
        self.step = None
        self.datasets = {}
        self.log_code = log_code
        self.metrics = {}
        self.name = name
        self.others = {}
        self.params = {}
        self.version = version + '-' + generate_guid()

        if in_notebook_environment():
            self.log_code = False
            notebook_id = get_notebook_id()

            if notebook_id is None:
                LOGGER.warning("Missing notebook id")

        self._start()

    def _on_end(self):
        if not self.commited:
            self.commit()

    def _start(self):

        self.start_dttm = datetime.now()

        try:
            atexit.register(self._on_end)
        except Exception:
            traceback.format_exc()
            LOGGER.error("Error while register on_end", exc_info=True)
            return None

        try:
            if self.log_code:
                self.set_code(self._get_source_code())
        except Exception:
            LOGGER.error("Error while getting source code", exc_info=True)

    def get_metric(self, name):
        return self.metrics[name]

    def get_parameter(self, name):
        return self.params[name]

    def get_other(self, name):
        return self.others[name]

    def log_other(self, key, value, step=None):
        LOGGER.debug("Log other value: %s %r %r", name, value, step)
        self.set_step(step)
        self.others[key] = value

    def log_others(self, dic, step=None):
        self.set_step(step)
        for k in dic:
            self.log_other(k, dic[k], self.step)

    def set_step(self, step):
        if step is not None:
            self.step = step

    def log_metric(self, name, value, step=None):
        LOGGER.debug("Log metric: %s %r %r", name, value, step)
        self.set_step(step)
        self.metrics[name] = value

    def log_parameter(self, name, value, step=None):
        LOGGER.debug("Log parameter: %s %r %r", name, value, step)
        self.set_step(step)
        self.params[name] = value

    def log_parameters(self, dic, step=None):
        self.set_step(step)

        for k in dic:
            self.log_parameter(k, dic[k], self.step)

    def log_metrics(self, dic, step=None):

        self.set_step(step)
        for k in dic:
            self.log_metric(k, dic[k], step)

    def log_dataset(self, name, shape=None):
        self.datasets[name] = shape

    def set_code(self, code):
        self.code = code

    def commit(self):
        Report.add_report(self.name,
                          Experiment.dict_to_string(self.params),
                          Experiment.dict_to_string(self.metrics),
                          Experiment.dict_to_string(self.others),
                          Experiment.dict_to_string(self.datasets),
                          self.start_dttm,
                          datetime.now(),
                          json.dumps(self.attachments),
                          self.code,
                          self.version)
        self.commited = True

    @staticmethod
    def dict_to_string(dictionary):
        return json.dumps(dictionary)

    @staticmethod
    def _get_source_code():
        """
        Inspects the stack to detect calling script.
        """

        for frame in inspect.stack(context=1):
            module = inspect.getmodule(frame[0])
            if "ml_tracker" != module.__name__:
                filename = module.__file__.rstrip("cd")
                with open(filename) as f:
                    return f.read()

        LOGGER.warning("Failed to find source code module")

    @staticmethod
    def _get_filename():

        if sys.argv:
            pathname = os.path.dirname(sys.argv[0])
            abs_path = os.path.abspath(pathname)
            filename = os.path.basename(sys.argv[0])
            full_path = os.path.join(abs_path, filename)
            return full_path

        return None
