# Pydoc-Markdown & Docusaurus

This directory shows how to use Pydoc-Markdown with [Docusaurus v2](https://v2.docusaurus.io/).

Steps that were done for this example:

1. Bootstrap a Docusaurus project:

```
$ npx @docusaurus/init@next init docusaurus-example classic
```

2. Bootstrap a Pydoc-Markdown configuration file for use with Docusaurus:

```
$ pydoc-markdown --bootstrap docusaurus
```

3. Update the Pydoc-Markdown configuration file.

    1. The Python loader must be able to find the `../src/school` package
    2. The `docs_base_path` must be updated to point to `docusaurus-example/docs`
    3. Set the `sidebar_top_level_label` to `null`

4. Update the `docusaurus-example/sidebar.js` to include `sidebar.json` created by Pydoc-Markdown:

```js
module.exports = {
  someSidebar: {
    "API Documentation": [
      require("./docs/reference/sidebar.json")
    ],
    Docusaurus: ['doc1', 'doc2', 'doc3'],
    Features: ['mdx'],
  },
};
```

5. Run Pydoc-Markdown to generate the Markdown files and `docs/reference/sidebar.json`.

```
$ pydoc-markdown
```

6. Run Docusaurus to preview the documentation:

```
$ cd docusaurus-example
$ yarn start
```
