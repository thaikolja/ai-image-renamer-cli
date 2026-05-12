#!/usr/bin/env python3
#
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

"""Dev entry point that adds src/ to sys.path then delegates to the CLI."""

import os
import sys

# Get the directory containing this main.py
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Add src/ to sys.path so the package can be imported without installation
_src_path = os.path.join(_current_dir, 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


def main():
    """Import and delegate to the CLI entry point."""
    from ai_image_renamer.cli import main as cli_main

    cli_main()


if __name__ == '__main__':
    main()
