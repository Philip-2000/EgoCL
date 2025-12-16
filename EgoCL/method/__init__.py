from .Dump import DumpMethod    #all the classes other than "Method" should NOT! be imported here, to avoid being accessed from outside directly
from .Video import VideoMethod  #although they still can be accessed via "EgoCL.method.Video.<class_name>", but at least, such a way greatly increases the difficulty of access.
#moreover, the base class Method in ./Base should not be imported here either, because they are only designed to be the parent class of other Method classes, but not to be used directly by other modules.

from ..paths import MEMORY_DIR, MEMORY_ROOT, CACHE_DIR, MODEL