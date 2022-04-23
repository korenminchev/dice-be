"""
Separated dependencies module. This is used instead of adding to __main__.py to prevent cyclic imports
"""

from odmantic import AIOEngine
from dice_be.managers.playground import Playground

engine = AIOEngine()
playground = Playground()
