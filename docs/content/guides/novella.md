@anchor getting-started
# Novella integration

  [Novella]: https://niklasrosenstein.github.io/novella/

[Novella][] is a Markdown pre-processor for static site generators. Pydoc-Markdown ships a Novella plugin that adds
two tags to your Markdown pages:

* `@pydoc <name>` inserts the generated API documentation for a module, class or function.
* `\{@pylink <name>}` links to an API object documented elsewhere on the site.

Use this when you want to write your documentation as ordinary Markdown files and embed API docs where they belong. This
documentation site is built that way.

## Installation

Pydoc-Markdown must be installed into the same environment as Novella:

```sh
pipx install novella
pipx inject novella pydoc-markdown
```

Novella's MkDocs template also needs `mkdocs` and `mkdocs-material` on your `PATH`.

## Project layout

```
docs/
├── build.novella      # Novella build script
├── mkdocs.yml         # optional; Novella creates a default one
└── content/           # your Markdown pages
    ├── index.md
    └── api.md
```

```py title="docs/build.novella"
template "mkdocs"

action "preprocess-markdown" {
  use "pydoc"
}
```

`template "mkdocs"` sets up a pipeline that copies `content/` and `mkdocs.yml` to a temporary directory, pre-processes
the Markdown and runs MkDocs. `use "pydoc"` enables the Pydoc-Markdown plugin in the pre-processing step. See the
[Novella templates](https://niklasrosenstein.github.io/novella/components/templates_/) for other options.

!!! note

    * The MkDocs template applies a default MkDocs configuration (Material theme and some extensions). Configure the
      `mkdocs-update-config` action to change or disable this.
    * If the build runs in a directory named `docs` or `documentation`, the plugin searches for Python code in `../src`
      and `..`; otherwise in `src` and `.`. See
      {@pylink pydoc_markdown.novella.preprocessor.PydocTagPreprocessor} for all options.

## Writing pages

```md title="docs/content/api.md"
# API Documentation

Some hand-written introduction.

\@pydoc my_module.SomeClass

See also \{@pylink my_module.helper}.
```

`@pydoc` renders the object with the {@pylink pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer}. Novella's
built-in tags work too; for example, `@cat` includes another file:

```md title="docs/content/index.md"
\@cat ../../README.md :with slice_lines = "2:"
```

## Building

Run Novella from the directory that contains `build.novella`:

```sh
novella            # build into _site/
novella --serve    # live preview
```

``` title="$ novella --help"
@shell novella --help
```

## Compared to a configuration file

With a [configuration file](configuration.md), all pages and their API contents are declared in one place and generated.
With Novella, every page is a real Markdown file:

* **Easier to follow**: the source tree mirrors the site.
* **Edit links work**: MkDocs' "edit this page" points at a real file.
* **Mixed content**: prose and generated API docs live on the same page.

If you want generated pages with Novella anyway (see [discussion #254](https://github.com/NiklasRosenstein/pydoc-markdown/discussions/254)),
the build script is code, so you can write them before the pre-processor runs:

```py title="docs/build.novella"
template "mkdocs"

def api_pages = {
  "SomeClass": "my_module.SomeClass",
  # ...
}

action "mkdocs-update-config" {
  site_name = "My module"
  profile = "readthedocs"
  update_with config -> {
    def items = []
    for title, package in api_pages.items():
      items.append({ title: 'api/{}.md'.format(package) })
    config['nav'].append({ 'API Documentation': items })
  }
}

action "preprocess-markdown" {
  use "pydoc"
}

do
  name: "generate-api-pages"
  closure: {
    # Make sure that this action runs before the Markdown preprocessors.
    precedes "preprocess-markdown"
  }
  action: {
    for title, package in api_pages.items():
      def path = directory / 'content' / 'api' / (package + '.md')
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text('---\ntitle: {}\n---\n@pydoc {}\n'.format(title, package))
  }
```
