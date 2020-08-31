

class School:
  """
  A school is a location for pupils to be taught by teachers.
  """

  #: The name of the school.
  name: str

  #: The name of the school's location.
  location: str

  def open(self) -> None:
    """
    Open the school. This method is usually called at 8am in the morning, but not if the
    director is late.
    """

  def close(self) -> None:
    """
    Close the school. This is usually called after all classes have ended.
    """
