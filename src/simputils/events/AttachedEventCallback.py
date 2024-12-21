from copy import copy


class AttachedEventCallback:

	_event = None
	_callback = None
	_args = None
	_kwargs = None

	def __init__(self, event, callback, *args, **kwargs):
		self._event = event
		self._callback = callback
		self._args = args
		self._kwargs = kwargs

	def __call__(self, *args, **kwargs):
		args = self._args + args
		kwargs = copy(self._kwargs)
		kwargs.update(kwargs)
		return self._callback(*args, **kwargs)
