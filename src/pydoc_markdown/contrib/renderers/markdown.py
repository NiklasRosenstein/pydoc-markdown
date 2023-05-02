# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import annotations

import dataclasses
import html
import io
import sys
import typing as t
from pathlib import Path

import docspec
from docspec_python import format_arglist
from yapf.yapflib.yapf_api import FormatCode  # type: ignore[import]

from pydoc_markdown.interfaces import (
    Context,
    Renderer,
    Resolver,
    ResolverV2,
    SingleObjectRenderer,
    SinglePageRenderer,
    SourceLinker,
)
from pydoc_markdown.util.docspec import ApiSuite, format_function_signature, is_method


def dotted_name(obj: docspec.ApiObject) -> str:
    return ".".join(x.name for x in obj.path)


@dataclasses.dataclass
class MarkdownRenderer(Renderer, SinglePageRenderer, SingleObjectRenderer):
    """
    Produces Markdown files. This renderer is often used by other renderers, such as
    #MkdocsRenderer and #HugoRenderer. It provides a wide variety of options to customize
    the generated Markdown files.

    ### Options
    """

    #: The name of the file to render to. If no file is specified, it will
    #: render to stdout.
    filename: t.Optional[str] = None

    #: The encoding of the output file. This is ignored when rendering to
    #: stdout.
    encoding: str = "utf-8"

    #: If enabled, inserts anchors before Markdown headers to ensure that
    #: links to the header work. This is enabled by default.
    insert_header_anchors: bool = True

    #: Generate HTML headers instead of Mearkdown headers. This is disabled
    #: by default.
    html_headers: bool = False

    #: Render names in headers as code (using backticks or `<code>` tags,
    #: depending on #html_headers). This is enabled by default.
    code_headers: bool = False

    #: Generate descriptive class titles by adding the word "Objects" if set to `True`. Otherwise,
    #: it can be a string that is appended or prepended (appended if the string begins with `$`).
    #: the class name. This is enabled by default.
    descriptive_class_title: t.Union[bool, str] = True

    #: Generate descriptivie module titles by adding the word "Module" before
    #: the module name. This is enabled by default.
    descriptive_module_title: bool = False

    #: Add the module name as a prefix to class & method names. This module name is
    #: also rendered as code if #code_headers is enabled. This is enabled
    #: by default.
    add_module_prefix: bool = True

    #: Add the class name as a prefix to method names. This class name is
    #: also rendered as code if #code_headers is enabled. This is enabled
    #: by default.
    add_method_class_prefix: bool = False

    #: Add the class name as a prefix to member names. This is enabled by
    #: default.
    add_member_class_prefix: bool = False

    #: Add the full module name as a prefix to the title of the header.
    #: This is disabled by default.
    add_full_prefix: bool = False

    #: If #add_full_prefix is enabled, this will result in the prefix to
    #: be wrapped in a `<sub>` tag.
    sub_prefix: bool = False

    #: Render the definition of data members as a code block. This is disabled
    #: by default.
    data_code_block: bool = False

    #: Max length of expressions. If this limit is exceeded, the remaining
    #: characters will be replaced with three dots. This is set to 100 by
    #: default.
    data_expression_maxlength: int = 100

    #: Render the class signature as a code block. This includes the "class"
    #: keyword, the class name and its bases. This is enabled by default.
    classdef_code_block: bool = True

    #: Render decorators before class definitions.
    classdef_with_decorators: bool = True

    #: Render classdef and function signature blocks in the Python help()
    #: style.
    signature_python_help_style: bool = False

    #: Render the function signature as a code block. This includes the "def"
    #: keyword, the function name and its arguments. This is enabled by
    #: default.
    signature_code_block: bool = True

    #: Render the function signature in the header. This is disabled by default.
    signature_in_header: bool = False

    #: Render the vertical bar '|' before function signature. This is enabled by default.
    signature_with_vertical_bar: bool = False

    #: Include the "def" keyword in the function signature. This is enabled
    #: by default.
    signature_with_def: bool = True

    #: Render the class name in the code block for function signature. Note
    #: that this results in invalid Python syntax to be rendered. This is
    #: disabled by default.
    signature_class_prefix: bool = False

    #: Render decorators before function definitions.
    signature_with_decorators: bool = True

    #: Render type hints for data elements in the header.
    render_typehint_in_data_header: bool = False

    #: Add the string "python" after the backticks for code blocks. This is
    #: enabled by default.
    code_lang: bool = True

    #: Render title of page at the beginning of the file.
    render_page_title: bool = False

    #: Render a table of contents at the beginning of the file.
    render_toc: bool = False

    #: The title of the "Table of Contents" header.
    render_toc_title: str = "Table of Contents"

    #: The maximum depth of the table of contents. Defaults to 2.
    toc_maxdepth: int = 2

    #: Render module headers. This is enabled by default.
    render_module_header: bool = True

    #: Custom template for module header.
    render_module_header_template: str = ""

    #: Render docstrings as blockquotes. This is disabled by default.
    docstrings_as_blockquote: bool = False

    #: Use a fixed header level for every kind of API object. The individual
    #: levels can be defined with #header_level_by_type.
    use_fixed_header_levels: bool = True

    #: Fixed header levels by API object type.
    header_level_by_type: t.Dict[str, int] = dataclasses.field(
        default_factory=lambda: {
            "Module": 1,
            "Class": 2,
            "Method": 4,
            "Function": 4,
            "Variable": 4,
        }
    )

    #: A plugin that implements the #SourceLinker interface to provide links to the
    #: source code of API objects. If this field is specified, the renderer will
    #: place links to the source code in the generated Markdown files.
    source_linker: t.Optional[SourceLinker] = None

    #: Allows you to define the position of the "view source" link in the Markdown
    #: file if a #source_linker is configured.
    # TODO: Validator.choices(["after signature", "before signature"])
    source_position: str = "after signature"

    #: Allows you to override how the "view source" link is rendered into the Markdown
    #: file if a #source_linker is configured. The default is `[[view_source]]({url})`.
    source_format: str = "[[view_source]]({url})"

    #: Escape html in docstring. Default to False.
    escape_html_in_docstring: bool = False

    #: Render Novella `@anchor` tags before headings.
    render_novella_anchors: bool = False

    #: Format code rendered into Markdown code blocks with YAPF.
    format_code: bool = True

    #: The style to format code as. This can be a YAPF builtin style name or point to
    #: a file relative to the context directory (usually the working directory).
    format_code_style: str = "pep8"

    def __post_init__(self) -> None:
        self._resolver = MarkdownReferenceResolver()

    def _is_method(self, obj: docspec.ApiObject) -> bool:
        return is_method(obj)

    def _format_arglist(self, func: docspec.Function) -> str:
        args = func.args[:]
        if self._is_method(func) and args and args[0].name == "self":
            args.pop(0)
        return format_arglist(args)

    def _render_toc(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        if level > self.toc_maxdepth:
            return
        object_id = self._resolver.generate_object_id(obj)
        title = self._escape(obj.name)
        if not self.add_module_prefix and isinstance(obj, docspec.Module):
            title = title.split(".")[-1]
        fp.write("  " * level + "* [{}](#{})\n".format(title, object_id))
        level += 1
        for child in getattr(obj, "members", []):
            self._render_toc(fp, level, child)

    def _render_header(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        if self.render_module_header_template and isinstance(obj, docspec.Module):
            fp.write(
                self.render_module_header_template.format(
                    module_name=obj.name, relative_module_name=obj.name.rsplit(".", 1)[-1]
                )
            )
            return

        object_id = self._resolver.generate_object_id(obj)
        if self.use_fixed_header_levels:
            # Read the header level based on the API object type. The default levels defined
            # in the field will act as a first fallback, the level of the object inside it's
            # hierarchy is the final fallback.
            header_levels = {
                **type(self).__dataclass_fields__["header_level_by_type"].default_factory(),  # type: ignore
                **self.header_level_by_type,
            }
            # Backwards compat for when we used "Data" instead of "Variable" which mirrors the docspec API
            header_levels["Variable"] = header_levels.get("Data", header_levels["Variable"])

            type_name = "Method" if self._is_method(obj) else type(obj).__name__
            level = header_levels.get(type_name, level)
        if self.insert_header_anchors and not self.html_headers:
            fp.write('<a id="{}"></a>\n\n'.format(object_id))
        if self.html_headers:
            header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
        else:
            header_template = level * "#" + " {title}"
        if self.render_novella_anchors:
            fp.write(f"@anchor pydoc:" + ".".join(x.name for x in obj.path) + "\n")
        fp.write(header_template.format(title=self._get_title(obj)))
        fp.write("\n\n")

    def _format_decorations(self, decorations: t.List[docspec.Decoration]) -> t.Iterable[str]:
        for dec in decorations:
            yield "@{}{}\n".format(dec.name, dec.args or "")

    def _yapf_code(self, code: str) -> str:
        if not self.format_code:
            return code
        style_file = Path(self._context.directory) / self.format_code_style
        style = str(style_file) if style_file.is_file() else self.format_code_style
        return FormatCode(code, style_config=style)[0]

    def _format_function_signature(
        self, func: docspec.Function, override_name: str | None = None, add_method_bar: bool = True
    ) -> str:
        parts: t.List[str] = []
        if self.signature_with_decorators:
            parts += self._format_decorations(func.decorations or [])
        if self.signature_python_help_style and not self._is_method(func):
            parts.append("{} = ".format(dotted_name(func)))
        parts += [x + " " for x in func.modifiers or []]
        if self.signature_with_def:
            parts.append("def ")
        if self.signature_class_prefix and self._is_method(func):
            parent = func.parent
            assert parent, func
            parts.append(parent.name + ".")
        parts.append((override_name or func.name))
        parts.append(format_function_signature(func, self._is_method(func)))
        result = "".join(parts)
        result = self._yapf_code(result + ": pass").rpartition(":")[0].strip()

        if add_method_bar and self._is_method(func):
            result = "\n".join(" | " + l for l in result.split("\n"))
        return result

    def _format_classdef_signature(self, cls: docspec.Class) -> str:
        bases = ", ".join(map(str, cls.bases or []))
        if cls.metaclass:
            if cls.bases:
                bases += ", "
            bases += "metaclass=" + str(cls.metaclass)
        code = "class {}({})".format(cls.name, bases)
        if self.signature_python_help_style:
            code = dotted_name(cls) + " = " + code
        code = self._yapf_code(code + ": pass").rpartition(":")[0].strip()

        if cls.decorations and self.classdef_with_decorators:
            code = "\n".join(self._format_decorations(cls.decorations)) + code
        return code

    def _format_data_signature(self, data: docspec.Variable) -> str:
        expr = str(data.value)
        code = self._yapf_code(data.name + " = " + expr).strip()
        if len(code) > self.data_expression_maxlength:
            code = code[: self.data_expression_maxlength] + " ..."
        return code

    def _render_signature_block(self, fp: t.TextIO, obj: docspec.ApiObject):
        if self.classdef_code_block and isinstance(obj, docspec.Class):
            code = self._format_classdef_signature(obj)
        elif self.signature_code_block and isinstance(obj, docspec.Function):
            code = self._format_function_signature(obj, add_method_bar=self.signature_with_vertical_bar)
        elif self.data_code_block and isinstance(obj, docspec.Variable):
            code = self._format_data_signature(obj)
        else:
            return
        fp.write("```{}\n".format("python" if self.code_lang else ""))
        fp.write(code)
        fp.write("\n```\n\n")

    def _render_object(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        if not isinstance(obj, docspec.Module) or self.render_module_header:
            self._render_header(fp, level, obj)

        render_view_source = not isinstance(obj, (docspec.Module, docspec.Variable))

        if render_view_source:
            url = self.source_linker.get_source_url(obj) if self.source_linker else None
            source_string = self.source_format.replace("{url}", str(url)) if url else None
            if source_string and self.source_position == "before signature":
                fp.write(source_string + "\n\n")

        self._render_signature_block(fp, obj)

        if render_view_source:
            if source_string and self.source_position == "after signature":
                fp.write(source_string + "\n\n")

        if obj.docstring:
            def escape_except_blockquotes(string: str) -> str:
                # Define regex patterns to match blockquotes
                single_quote_pattern = r"`[^`]*`"
                triple_quote_pattern = r"```[\s\S]*?```"

                # Find all blockquotes in the string
                blockquote_matches = re.findall(f"({triple_quote_pattern}|{single_quote_pattern})", string)

                # Replace all blockquotes with placeholder tokens to preserve their contents
                for i, match in enumerate(blockquote_matches):
                    string = string.replace(match, f"BLOCKQUOTE_TOKEN_{i}")

                # Escape the remaining string
                escaped_string = html.escape(string)

                # Replace the placeholder tokens with their original contents
                for i, match in enumerate(blockquote_matches):
                    escaped_string = escaped_string.replace(f"BLOCKQUOTE_TOKEN_{i}", match)

                print("///", string, "\n|||", escaped_string)
                return escaped_string

            docstring = escape_except_blockquotes(obj.docstring.content) if self.escape_html_in_docstring else obj.docstring.content
            lines = docstring.split("\n")
            if self.docstrings_as_blockquote:
                lines = ["> " + x for x in lines]
            fp.write("\n".join(lines))
            fp.write("\n\n")

    def _render_recursive(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        self._render_object(fp, level, obj)
        level += 1
        for member in getattr(obj, "members", []):
            self._render_recursive(fp, level, member)

    def _get_title(self, obj: docspec.ApiObject) -> str:
        title = obj.name
        if (self.add_method_class_prefix and self._is_method(obj)) or (
            self.add_member_class_prefix and isinstance(obj, docspec.Variable)
        ):
            title = (obj.parent.name + "." + title) if obj.parent else title
        elif self.add_full_prefix and not self._is_method(obj):
            title = dotted_name(obj)
        if not self.add_module_prefix and isinstance(obj, docspec.Module):
            title = title.split(".")[-1]
        if isinstance(obj, docspec.Function):
            if self.signature_in_header:
                title += "(" + self._format_arglist(obj) + ")"

        if isinstance(obj, docspec.Variable) and obj.datatype and self.render_typehint_in_data_header:
            if self.code_headers:
                title += f": {obj.datatype}"
            elif self.html_headers:
                title += f": <code>{obj.datatype}</code>"
            else:
                title += f": `{obj.datatype}`"

        if self.code_headers:
            if self.html_headers or self.sub_prefix:
                if self.sub_prefix and "." in title:
                    prefix, title = title.rpartition(".")[::2]
                    title = "<sub>{}.</sub>{}".format(prefix, title)
                title = "<code>{}</code>".format(title)
            else:
                title = "`{}`".format(title)
        elif not self.html_headers:
            title = self._escape(title)
        if isinstance(obj, docspec.Module) and self.descriptive_module_title:
            title = "Module " + title
        if isinstance(obj, docspec.Class) and self.descriptive_class_title:
            if self.descriptive_class_title is True:
                title += " Objects"
            elif self.descriptive_class_title is False:
                pass
            elif self.descriptive_class_title.startswith("$"):
                title += self.descriptive_class_title[1:]
            else:
                title = self.descriptive_class_title + title
        return title

    def _escape(self, s):
        return s.replace("_", "\\_").replace("*", "\\*")

    def render_to_string(self, modules: t.List[docspec.Module]) -> str:
        fp = io.StringIO()
        self.render_single_page(fp, modules)
        return fp.getvalue()

    def _render_to_stream(self, modules: t.List[docspec.Module], stream: t.TextIO):
        return self.render_single_page(stream, modules)

    # SinglePageRenderer

    def render_single_page(
        self, fp: t.TextIO, modules: t.List[docspec.Module], page_title: t.Optional[str] = None
    ) -> None:
        if self.render_page_title:
            fp.write("# {}\n\n".format(page_title))

        if self.render_toc:
            if self.render_toc_title:
                if self.render_page_title:
                    # set to level2 since level1 is page title
                    fp.write("## {}\n\n".format(self.render_toc_title))
                else:
                    fp.write("# {}\n\n".format(self.render_toc_title))

            for m in modules:
                self._render_toc(fp, 0, m)
            fp.write("\n")
        for m in modules:
            self._render_recursive(fp, 1, m)

    # SingleObjectRenderer

    def render_object(self, fp: t.TextIO, obj: docspec.ApiObject, options: t.Dict[str, t.Any]) -> None:
        self._render_recursive(fp, 0, obj)

    # Renderer

    def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
        """
        Returns a simple #Resolver implementation. Finds cross-references in the same file.
        """

        return self._resolver

    def render(self, modules: t.List[docspec.Module]) -> None:
        if self.filename is None:
            self._render_to_stream(modules, sys.stdout)
        else:
            with io.open(self.filename, "w", encoding=self.encoding) as fp:
                self._render_to_stream(modules, t.cast(t.TextIO, fp))

    # PluginBase

    def init(self, context: Context) -> None:
        if self.source_linker:
            self.source_linker.init(context)
        self._context = context


@dataclasses.dataclass
class MarkdownReferenceResolver(Resolver, ResolverV2):

    local: bool = True
    global_: bool = False

    def generate_object_id(self, obj: docspec.ApiObject) -> str:
        return ".".join(o.name for o in obj.path)

    def _resolve_reference_in_members(
        self, obj: t.Optional[docspec.ApiObject], ref: t.List[str]
    ) -> t.Optional[docspec.ApiObject]:
        if not obj:
            return None
        for part_name in ref:
            obj = docspec.get_member(obj, part_name)
            if not obj:
                return None
        return obj

    def _resolve_local_reference(
        self, scope: docspec.ApiObject, ref_split: t.List[str]
    ) -> t.Optional[docspec.ApiObject]:
        obj: t.Optional[docspec.ApiObject] = scope
        while obj:
            resolved = self._resolve_reference_in_members(obj, ref_split)
            if resolved:
                return resolved
            obj = obj.parent
        return None

    # Resolver

    def resolve_ref(self, scope: docspec.ApiObject, ref: str) -> t.Optional[str]:
        target = self._resolve_local_reference(scope, ref.split("."))
        if target:
            return "#" + self.generate_object_id(target)
        return None

    # ResolverV2

    def resolve_reference(self, suite: ApiSuite, scope: docspec.ApiObject, ref: str) -> t.Optional[docspec.ApiObject]:
        """Resolves the reference by searching in the members of *scope* or any of its parents."""

        # TODO (@NiklasRosenstein): Support resolving indirections

        ref_split = ref.split(".")

        resolved = self._resolve_local_reference(scope, ref_split)
        if resolved:
            return resolved

        if self.global_:

            def _recurse(obj: docspec.ApiObject) -> t.Optional[docspec.ApiObject]:
                resolved = self._resolve_reference_in_members(obj, ref_split)
                if resolved:
                    return resolved
                if isinstance(obj, docspec.HasMembers):
                    for member in obj.members:
                        resolved = _recurse(member)
                        if resolved:
                            return resolved
                return None

            for module in suite:
                resolved = _recurse(module)
                if resolved:
                    return resolved

        return None
