
from ._teacher import Teacher


class Class:
  """
  A class is a recurring session for pupils to learn from teachers.
  """

  #: The topic of the class.
  topic: str

  #: The teacher that is holding the class.
  teacher: Teacher
