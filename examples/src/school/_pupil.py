
from typing import List
from ._class import Class
from ._person import Person


class Pupil(Person):
  """
  Pupils attend classes to learn things.
  """

  #: A list of classes that the pupil attends.
  classes: List[Class]
