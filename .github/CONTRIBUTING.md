# Contributing to Pydoc-Markdown

  [unreleased]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.changelog/_unreleased.toml
  [Discussions]: https://github.com/NiklasRosenstein/pydoc-markdown/discussions
  [Slam]: https://niklasrosenstein.github.io/slam/

You are welcome to contribute Pydoc-Markdown. Feel free to use [Discussions][] if you have any questions before
creating a Pull Request.

When you create a Pull Request, please make sure that you add an entry for the
[`.changelog/_unreleased.toml`][unreleased] file. Please use [Slam][] to create the changelog entry.

    $ slam changelog add -t <type> -d <changelog message> [--issue <issue_url>]

After you create the pull request, GitHub Actions will take care of injecting the PR URL into the changelog entry.
