#  AI Image Renamer
#
#  Copyright (C) 2026 Kolja Nolte
#  https://www.kolja-nolte.com
#  kolja.nolte@gmail.com
#
#  This work is licensed under the MIT License. You are free to use, modify, and distribute this work, provided that you include the copyright notice and this permission notice in all copies or substantial portions of the work. For more information, visit: https://opensource.org/licenses/MIT
#
#  @author      Kolja Nolte
#  @email       kolja.nolte@gmail.com
#  @license     MIT
#  @date        2026
#  @website     https://docs.kolja-nolte.com/ai-image-renamer
#  @repository  https://gitlab.com/thaikolja/ai-image-renamer

"""Package init and public API exports."""

from importlib.metadata import PackageNotFoundError, version

# Package metadata constants
_PACKAGE_NAME = 'ai-image-renamer'
_FALLBACK_VERSION = '1.1.0'

# Try to fetch version from installed package metadata
try:
    __version__ = version(_PACKAGE_NAME)
except PackageNotFoundError:
    __version__ = _FALLBACK_VERSION

# Import public API components
from .cli import main
from .renamer import ImageRenamer
from .utils import verify_image_file, encode_image, sanitize_image_path, get_words

# Define public interface for star imports
__all__ = [
    '__version__',
    'ImageRenamer',
    'main',
    'verify_image_file',
    'encode_image',
    'sanitize_image_path',
    'get_words',
]
