from pydocmd.preprocessors.rst import Preprocessor as RSTPreprocessor
from pydocmd.preprocessors.google import Preprocessor as GooglePreprocessor


class Preprocessor(object):
    """
    This class implements the preprocessor for restructured text and google.
    """

    def __init__(self, config=None):
        self.config = config
        self._google_preprocessor = GooglePreprocessor(config)
        self._rst_preprocessor = RSTPreprocessor(config)

    def preprocess_section(self, section):
        """
        Preprocessors a given section into it's components.
        """
        lines = [line.strip() for line in section.content.split('\n')]
        google_keywords = self._google_preprocessor.keywords_map.keys()
        for google_keyword in google_keywords:
            if google_keyword in lines:
                return self._google_preprocessor.preprocess_section(section)

        return self._rst_preprocessor.preprocess_section(section)

    @staticmethod
    def _append_section(lines, key, sections):
        section = sections.get(key)
        if not section:
            return

        if lines and lines[-1]:
            lines.append('')

        # add an extra line because of markdown syntax
        lines.extend(['**{}**:'.format(key), ''])
        lines.extend(section)
