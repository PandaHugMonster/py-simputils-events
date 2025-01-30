from typing import Callable, Union, OrderedDict

from simputils.events.auxiliary.AttachedEventHandler import AttachedEventHandler
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventHandler import BasicEventHandler
from simputils.events.generic.BasicEventRuntime import BasicEventRuntime

EventHandlerType = Union[BasicEventHandler, Callable]
EventRuntimeType = Union[type[BasicEventRuntime], BasicEventRuntime]
EventDefinitionType = Union[type[BasicEventDefinition], BasicEventDefinition]
EventRefType = Union[str, type]
EventPriorityPair = OrderedDict[int, AttachedEventHandler]
# EventPriorityPair = list[int, AttachedEventHandler]
