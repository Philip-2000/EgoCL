
LOAD_STYLE = ("FORCE_CREATE", "LOAD_CREATE", "FORCE_LOAD")
# "FORCE_CREATE": always create new element, even if already exists
# "LOAD_CREATE": load existing element if exists, otherwise create new one
# "FORCE_LOAD": always load existing element, error if not exists
from .Execution import Execution
from .Question import Questions

