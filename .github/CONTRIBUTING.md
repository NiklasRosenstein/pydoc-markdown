# Contributing to Pydoc-Markdown

  [unreleased]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.changelog/_unreleased.yml
  [Discussions]: https://github.com/NiklasRosenstein/pydoc-markdown/discussions

You are welcome to contribute Pydoc-Markdown. Feel free to use [Discussions][] if you have any questions before creating a Pull Request.

When you create a Pull Request, please make sure that you add an entry for the [`.changelog/_unreleased.yml`][unreleased] file. If the file
does not already exists in your fork, create it using the below template:

```yml
changes:
- type: fix  # or one of improvement, change, breaking_change, refactor, feature, docs, tests
  component: general  # or docusaurus, hugo, markdown, or something else applicable
  description: 'Description here, supports `backticks` for monospace rendering. (@YourGithubUsername)'
  fixes: [ '#XYZ' ]  # A list of GitHub issues resolved by this changelog, can be empty. Can point to another GitHub repository, e.g. NiklasRosenstein/databind#12
```

The changelog format must be recognizable by [Shut](https://shut.readthedocs.io/en/latest/).
