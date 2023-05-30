# Contributing to Pydoc-Markdown

  [0]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.changelog/_unreleased.toml
  [1]: https://github.com/NiklasRosenstein/pydoc-markdown/discussions
  [Slam]: https://niklasrosenstein.github.io/slap/

Contributions to Pydoc-Markdown are very welcome!

If you want to talk about a potential contribution before investing any time, please do create a new topic on
[GitHub Discussions][0].

## Pull request requirements

* Please look to adhere to the existing code style (2-space indendation, 120 character line length limit)
* Pull requests should contain at least one new changelog entry unless the change is trivial (see below for details)

## Changelog entries

Pydoc-Markdown uses [Slap][] to manage changelogs. You should use the Slam CLI to add a new changelog entry, otherwise
you need to manually generate a UUID-4.

    $ slap changelog add -t <type> -d <changelog message> [--issue <issue_url>]

After you create the pull request, GitHub Actions will take care of injecting the PR URL into the changelog entry.

For a full list of accepted changelog types see [here](https://niklasrosenstein.github.io/slap/commands/changelog/)