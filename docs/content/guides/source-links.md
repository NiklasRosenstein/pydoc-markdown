# Source links

Renderers built on the [Markdown renderer](../reference/renderers/markdown.md) (`markdown`, `mkdocs`, `hugo`,
`docusaurus`) can add a "view source" link to every class and function. Configure a **source linker** on the Markdown
renderer:

=== "markdown renderer"

    ```yaml
    renderer:
      type: markdown
      source_linker:
        type: github
        repo: my-org/my-project
    ```

=== "mkdocs / hugo renderer"

    ```yaml
    renderer:
      type: mkdocs
      markdown:
        source_linker:
          type: github
          repo: my-org/my-project
    ```

=== "docusaurus renderer"

    ```yaml
    renderer:
      type: docusaurus
      markdown:
        source_linker:
          type: github
          repo: my-org/my-project
    ```

Links point at the current Git commit, so they keep working after the code moves on. Set `use_branch: true` to link to
the current branch instead.

## Available source linkers

| `type` | Host default | URL produced |
| --- | --- | --- |
| `github` | `github.com` | `https://{host}/{repo}/blob/{sha}/{path}#L{lineno}` |
| `gitlab` | `gitlab.com` | `https://{host}/{repo}/-/blob/{sha}/{path}#L{lineno}` |
| `gitea` | `gitea.com` | `https://{host}/{repo}/src/commit/{sha}/{path}#L{lineno}` |
| `bitbucket` | `bitbucket.org` | `https://{host}/{repo}/src/{sha}/{path}#lines-{lineno}` |
| `git` | — | your own `url_template` |

For a self-hosted instance, set `host`:

```yaml
source_linker:
  type: gitlab
  host: gitlab.example.com
  repo: team/project
```

For anything else, use `git` with a Python format string. The variables `path`, `sha` and `lineno` are available:

```yaml
source_linker:
  type: git
  url_template: https://code.example.com/project/{path}?at={sha}#line-{lineno}
```

## Options

All source linkers accept:

* `root`: the repository root, relative to the directory that contains the configuration file. Detected from Git if
  not set.
* `use_branch`: link to the branch name instead of the commit SHA. Default: `false`.

The Markdown renderer controls where and how the link appears:

* `source_position`: `after signature` (default) or `before signature`.
* `source_format`: the Markdown for the link; `{url}` is replaced. Default: `[[view_source]]({url})`.

See the [source linker reference](../reference/source-linkers.md) for details.
