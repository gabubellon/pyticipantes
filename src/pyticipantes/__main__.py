"""Inicia o servidor web: pyticipantes [--host 127.0.0.1] [--porta 8000]."""
import argparse
import os

from .app import servir


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyticipantes", description=__doc__)
    parser.add_argument("--host", default=os.getenv("PYTICIPANTES_HOST", "127.0.0.1"),
                        help="interface de escuta (padrão 127.0.0.1; 0.0.0.0 em servidor/Docker)")
    parser.add_argument("--porta", type=int, default=int(os.getenv("PYTICIPANTES_PORTA", "8000")))
    args = parser.parse_args()
    servir(args.host, args.porta)


if __name__ == "__main__":
    main()
