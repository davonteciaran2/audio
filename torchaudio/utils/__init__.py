from torchaudio._internal import module_utils as _mod_utils

from . import sox_utils
from .download import download_asset

if _mod_utils.is_sox_available():
    sox_utils.set_verbosity(1)


__all__ = [
    "download_asset",
    "sox_utils",
]
