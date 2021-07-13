import errno
import inspect
import logging
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Tuple, Union

import ciptools.resources

logger = logging.getLogger(__name__)


# this configuration loader was taken from the Flask configuration loader
# the original can be found here: https://github.com/pallets/flask/blob/main/src/flask/config.py
class ConfigurationLoader(dict):
    def __init__(self, defaults: dict = None):
        dict.__init__(self, defaults or {})

    def from_string(self, data: str):
        d = ModuleType("configuration")
        d.__file__ = "string"
        exec(compile(data, "string", "exec"), d.__dict__)  # noqa S102
        self.from_object(d)
        return True

    def from_pyfile(self, filename: Union[str, Path], silent: bool = False):
        d = ModuleType("configuration")
        d.__file__ = filename
        try:
            with open(filename, mode="rb") as config_file:
                exec(compile(config_file.read(), filename, "exec"), d.__dict__)  # noqa S102
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            e.strerror = "unable to load configuration file ({})".format(e.strerror)
            raise
        self.from_object(d)
        return True

    def from_object(self, obj: Any):
        if isinstance(obj, str):
            obj = self.import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    @staticmethod
    def import_string(import_name, silent=False):
        import_name = str(import_name).replace(":", ".")
        try:
            try:
                __import__(import_name)
            except ImportError:
                if "." not in import_name:
                    raise
            else:
                return sys.modules[import_name]

            module_name, obj_name = import_name.rsplit(".", 1)
            module = __import__(module_name, globals(), locals(), [obj_name])
            try:
                return getattr(module, obj_name)
            except AttributeError as e:
                raise ImportError(e) from None

        except ImportError:
            if not silent:
                raise


def load_configuration(package: str = None, path: str = None, environment: str = None) -> Tuple[str, ConfigurationLoader]:
    configuration = ConfigurationLoader()

    if environment is None:
        environment = os.environ.get("ENVIRONMENT") or "development"

    if package is None:
        if path is None:
            path = os.environ.get("CONFIGURATIONS")

        if path is None:
            # load from a package called "{calling_package}.configurations"
            calling_package = inspect.currentframe().f_back.f_globals["__package__"]
            if calling_package:
                package = ".".join([calling_package, "configurations"])
            else:
                package = "configurations"

            configuration.from_string(ciptools.resources.files(package).joinpath(f"{environment}.conf").read_text())
        else:
            path = os.path.join(path, f"{environment}.conf")
            logger.info(f"loading configuration from '{path}'")
            configuration.from_pyfile(path)

    else:
        configuration.from_string(ciptools.resources.files(package).joinpath(f"{environment}.conf").read_text())

    return environment, configuration
