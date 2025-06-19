from shutil import get_terminal_size

from ee_crm.cli_interface.views.view_base import BaseView


class ErrorView(BaseView):
    max_width = 64
    delimitation = "▓"

    def __init__(self, error_catch=None):
        self.error_catch = error_catch
        if error_catch:
            self.error_msg = error_catch.args[0] \
                if any(error_catch.args) else ''
            self.error_type = type(error_catch).__name__
            self.error_threat = error_catch.threat.capitalize()
            self.error_level = error_catch.level
            self.tips = error_catch.tips
            self.display_func = self.set_display_func(error_catch.threat)

    def set_display_func(self, threat):
        if threat == "error":
            return self.error
        elif threat == "warning":
            return self.warning
        else:
            return self.echo

    def _calculate_width(self):
        width = min(get_terminal_size().columns, self.max_width)
        return width

    def _create_blank_line(self, width):
        return (f"{self.delimitation * 2}"
                f"{" " * (width-4)}"
                f"{self.delimitation * 2}")

    def _create_header(self, width):
        title = f" {" ".join(self.error_threat.upper())} "
        half_line = (width - len(title)) // 2
        leftover = (width - len(title)) % 2
        full_line = self.delimitation * width
        title_line = (f"{half_line * self.delimitation}"
                      f"{title}"
                      f"{(leftover + half_line) * self.delimitation}")
        blank_line = self._create_blank_line(width)
        return full_line, title_line, full_line, blank_line

    def _create_footer(self, width):
        blank_line = (f"{self.delimitation * 2}"
                      f"{" " * (width-4)}"
                      f"{self.delimitation * 2}")
        full_line = self.delimitation * width
        return blank_line, full_line

    def _create_border(self, side="left"):
        if side == "left":
            return f"{self.delimitation * 2} "
        else:
            return f" {self.delimitation * 2}"

    @staticmethod
    def _transform_text_to_chunks(text, width):
        available_width = width - 6
        return [text[i:i+available_width]
                for i in range(0, len(text), available_width)]

    @staticmethod
    def _normalize_chunks(chunks, width):
        last_chunk = chunks[-1]
        blanks = (width - 6) - len(last_chunk)
        if blanks > 0:
            chunks[-1] = last_chunk + " " * blanks
        return chunks

    def _transform_row_to_lines(self, text, width):
        chunks = self._transform_text_to_chunks(text, width)
        return self._normalize_chunks(chunks, width)

    def _create_body(self, width):
        err_name = f"{self.error_threat} name : {self.error_type}"
        err_threat = f"{self.error_threat} at the {self.error_level} level"
        err_message = f"Message : {self.error_msg}"
        err_tips = f"Tips : {self.tips}"

        chunk_name = self._transform_row_to_lines(err_name, width)
        chunk_threat = self._transform_row_to_lines(err_threat, width)
        chunk_message = self._transform_row_to_lines(err_message, width)
        chunk_tips = self._transform_row_to_lines(err_tips, width)

        return [*chunk_name, *chunk_threat], [*chunk_message, *chunk_tips]

    def display_error(self):
        width = self._calculate_width()
        header = self._create_header(width)
        for elem in header:
            self.display_func(elem)

        body_err, body_info = self._create_body(width)
        border_left = self._create_border(side="left")
        border_right = self._create_border(side="right")
        for line in body_err:
            self.display_func(border_left, nl=False)
            self.display_func(line, nl=False)
            self.display_func(border_right)

        self.display_func(self._create_blank_line(width))

        for line in body_info:
            self.display_func(border_left, nl=False)
            self.echo(line, nl=False)
            self.display_func(border_right)

        footer = self._create_footer(width)
        for elem in footer:
            self.display_func(elem)
