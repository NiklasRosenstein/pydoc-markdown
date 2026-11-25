# Pydoc-Markdown & Docusaurus

This directory shows how to use Pydoc-Markdown with [Docusaurus](https://docusaurus.io/) 3.

## Try it

```sh
pydoc-markdown            # writes docusaurus-example/docs/reference/
cd docusaurus-example
npm install
npm start
```

## How it was set up

1. Bootstrap a Docusaurus project:

   ```sh
   npx create-docusaurus@3 docusaurus-example classic --javascript
   ```

2. Bootstrap a Pydoc-Markdown configuration for Docusaurus and adjust it (see [`pydoc-markdown.yml`](pydoc-markdown.yml)):

   ```sh
   pydoc-markdown --bootstrap docusaurus
   ```

   * The Python loader's `search_path` points to `../src` so it finds the `school` package.
   * `docs_base_path` points to `docusaurus-example/docs`.
   * `sidebar_top_level_label` is `null`, so the sidebar starts at the top-level package.

3. Include the generated `docs/reference/sidebar.json` in
   [`docusaurus-example/sidebars.js`](docusaurus-example/sidebars.js):

   ```js
   import apiReference from './docs/reference/sidebar.json';

   const sidebars = {
     tutorialSidebar: [
       'intro',
       {type: 'category', label: 'API Documentation', items: [apiReference]},
     ],
   };
   ```

4. Stop Docusaurus from ignoring files that start with an underscore (such as `_person.md` for the `school._person`
   module). In [`docusaurus-example/docusaurus.config.js`](docusaurus-example/docusaurus.config.js), set the docs
   plugin's [`exclude`](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-content-docs#exclude) option so it
   leaves out only test files:

   ```js
   exclude: ['**/*.test.{js,jsx,ts,tsx}', '**/__tests__/**'],
   ```

5. Ignore the generated `docs/reference/` directory in `docusaurus-example/.gitignore`.
