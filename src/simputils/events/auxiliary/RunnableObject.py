from abc import ABCMeta, abstractmethod


class RunnableObject(metaclass=ABCMeta):

	@abstractmethod
	def run(self, *args, **kwargs):
		pass

	def __call__(self, *args, **kwargs):
		return self.run(*args, **kwargs)
