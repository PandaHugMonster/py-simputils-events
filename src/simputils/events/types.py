from typing import Callable, Union, OrderedDict

from simputils.events.AttachedEventHandler import AttachedEventHandler
from simputils.events.generic.BasicEventDefinition import BasicEventDefinition
from simputils.events.generic.BasicEventHandler import BasicEventHandler
from simputils.events.generic.BasicRuntime import BasicRuntime

EventHandlerType = Union[BasicEventHandler, Callable]
EventRuntimeType = Union[type[BasicRuntime], BasicRuntime]
EventDefinitionType = Union[type[BasicEventDefinition], BasicEventDefinition]
EventRefType = Union[str, type]
EventPriorityPair = OrderedDict[int, AttachedEventHandler]
# EventPriorityPair = list[int, AttachedEventHandler]
