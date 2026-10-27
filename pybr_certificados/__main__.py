"""Inicia o servidor web: python -m pybr_certificados [--porta 8000]"""
import argparse

from .app import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="pybr_certificados", description=__doc__)
    parser.add_argument("--porta", type=int, default=8000)
    main(parser.parse_args().porta)
