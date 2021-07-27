import os

from api import metatrader5 as mt
from api import streamdeck as sd


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    cls()
    mt.connect()
    sd.streamdeck()


if __name__ == "__main__":
    main()
