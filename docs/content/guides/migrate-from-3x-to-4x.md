# Migrate from 3.x to 4.x

In version 4.x, Pydoc-Markdown migrated from using the `nr.databind.core` and `nr.databind.json` libraries for
config deserialization to the `databind.core 1.x` and `databind.json 1.x` packages. It also dropped use of the
`nr.interface` library and all interfaces are now defined as ABCs. **This change does not affect the requirements
for your Pydoc-Markdown configuration files**, but it will require a change if you have developed your own plugins.
Note also that starting with version 4.x, Pydoc-Markdown requires Python 3.7 or newer (before it was Python 3.6
or newer), but it is still capable of parsing older Python source code (incl. Python 2).

This is how your plugin may be defined for compatibility with Pydoc-Markdown 3.x where you use `nr.databind.core`:

```py
from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Loader

@implements(Loader)
class MyLoaderPlugin(Struct):
  directories_to_search = Field([str], default=['.'])

  def load(self) -> t.Iterable[docspec.Module]:
    # ...
```

Because Pydoc-Markdown 4.x now uses `databind.core 1.x` and the use of ABCs, you need to use Python dataclasses instead
to define options for your plugin and inherit directly from the `Loader` class:

```py
import dataclasses
import typing as t
from pydoc_markdown.interfaces import Loader

@dataclasses.dataclass
class MyLoaderPlugin(Loader):
  directories_to_search: t.List[str] = dataclasses.field(default_factory=lambda: ['.'])

  def load(self) -> t.Iterable[docspec.Module]:
    # ...
```

This _should_ not affect how your plugin is deserialized and loaded. The entire Pydoc-Markdown codebase with it's
built-in plugins have been migrated to this format and all config deserialization continues to work the same as it
did before. Unless you are doing something very specific with `nr.databind.core` or `nr.databind.json`, you should
be good.
