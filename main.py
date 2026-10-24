import os
import sys

from veda.cli import build_app
from veda.exceptions import VedaError


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        app = build_app(base_dir)
    except VedaError as error:
        print(f"Startup error: {error}")
        return 1
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
