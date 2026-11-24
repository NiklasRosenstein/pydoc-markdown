# Changelog

@shell cd .. && towncrier build --draft --version Unreleased 2>/dev/null | sed -E '1s/ \([0-9-]+\)$//' && sed '1,/towncrier release notes start/d' CHANGELOG.md
