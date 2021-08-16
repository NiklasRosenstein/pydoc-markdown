
import re
import typing as t
from pathlib import Path
import yaml


class Case(t.NamedTuple):
  filename: Path
  config: t.Dict[str, t.Any]
  code: str
  output: str

  def __repr__(self) -> str:
    return f'Case(filename={str(self.filename)!r})'


def assert_text_equals(a: str, b: str) -> None:
  assert '\n'.join([x.rstrip() for x in a.strip().split('\n')]) == \
         '\n'.join([x.rstrip() for x in b.strip().split('\n')])


def load_testcases(folder_name: str) -> t.List[Case]:
  files = [f for f in (Path(__file__).parent / 'testcases' / folder_name).iterdir() if f.suffix == '.txt']
  result: t.List[Case] = []
  for path in files:
    parts = re.split(r'-{4,}\n', path.read_text())
    assert parts[0] == ''
    config, code, output = parts[1:]
    config = yaml.safe_load(config) if config.strip() else {}
    result.append(Case(path, config, code, output))
  return result
