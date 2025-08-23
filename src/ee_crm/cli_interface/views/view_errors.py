from shutil import get_terminal_size

from ee_crm.cli_interface.views.view_base import BaseView


class ErrorView(BaseView):
    max_width = 64
    delimitation = "▓"

    def __init__(self, error_catch=None):
        if error_catch:
            self.error_msg = error_catch.args[0] \
                if any(error_catch.args) else ''
            self.error_type = type(error_catch).__name__
            self.error_threat = error_catch.threat.capitalize()
            self.error_level = error_catch.level
            self.tips = error_catch.tips
            self.display_func = self.set_display_func(error_catch.threat)

    def set_display_func(self, threat):
        """Method that use the appropriate methods to display the
        error. The methods are from the parent class BaseView.

        Args:
            threat (str): label level of the error.

        Returns:
            Callable: The display function used for the error.
                One of (error (red), warning (yellow) or echo (white)).
        """
        if threat == "error":
            return self.error
        elif threat == "warning":
            return self.warning
        else:
            return self.echo

    def _calculate_width(self):
        """Calculate the width of the error message window dynamically.

        Returns:
            int: The width of the error message window.
        """
        width = min(get_terminal_size().columns, self.max_width)
        return width

    def _create_blank_line(self, width):
        """Create a blank line with left and right border.

        Args:
            width (int): The width of the error message window.

        Returns:
            str: The blank line, ready to be printed.
        """
        return (f"{self.delimitation * 2}"
                f"{" " * (width-4)}"
                f"{self.delimitation * 2}")

    def _create_header(self, width):
        """Create the header block of the error message window.

        Args:
            width (int): The width of the error message window.

        Returns:
            tuple[str]: The header block of the error message window.
        """
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
        """Create the footer block of the error message window.

        Args:
            width (int): The width of the error message window.

        Returns:
            tuple[str]: The footer block of the error message window.
        """
        blank_line = (f"{self.delimitation * 2}"
                      f"{" " * (width-4)}"
                      f"{self.delimitation * 2}")
        full_line = self.delimitation * width
        return blank_line, full_line

    def _create_border(self, side="left"):
        """Create the border of the body of the error message window.

        Args:
            side (str): either left or right side border.

        Returns:
            str: The border of the error message window.
        """
        if side == "left":
            return f"{self.delimitation * 2} "
        else:
            return f" {self.delimitation * 2}"

    @staticmethod
    def _transform_text_to_chunks(text, width):
        """Transform a string to a list of string of size width minus the
        borders size.

        Args:
            text (str): The text to be transformed.
            width (int): The width of the error message window.

        Returns:
            list[str]: The transformed text.
        """
        available_width = width - 6
        return [text[i:i+available_width]
                for i in range(0, len(text), available_width)]

    @staticmethod
    def _fill_last_chunks(chunks, width):
        """Fill the last chunks of the error message window with blanks.

        Args:
            chunks (list[str]): The chunks of the message.
            width (int): The width of the error message window.

        Returns:
            list[str]: The transformed text of the same size string.
        """
        last_chunk = chunks[-1]
        blanks = (width - 6) - len(last_chunk)
        if blanks > 0:
            chunks[-1] = last_chunk + " " * blanks
        return chunks

    def _transform_row_to_lines(self, text, width):
        """Transform a string to a list of string of identical size
        depending on the width of the error message windows.

        Args:
            text (str): The text to be transformed.
            width (int): The width of the error message window.

        Returns:
            list[str]: The transformed text.
        """
        chunks = self._transform_text_to_chunks(text, width)
        return self._fill_last_chunks(chunks, width)

    def _add_border(self, lines):
        """Add the border of the error message window to the lines.

        Args:
            list[str]: The lines of the error message window.

        Returns:
            list[str]: The lines of the error message window with
                borders.
        """
        border_left = self._create_border(side="left")
        border_right = self._create_border(side="right")
        return [f"{border_left}{line}{border_right}" for line in lines]

    def _build_body_sections(self, width):
        """Build the body sections of the error message window.

        Args:
            width (int): The width of the error message window.

        Returns:
            tuple[list[str]]: The body sections content.
        """
        err_name = f"{self.error_threat} name : {self.error_type}"
        err_threat = f"{self.error_threat} at the {self.error_level} level"
        err_message = f"Message : {self.error_msg}"
        err_tips = f"Tips : {self.tips}"

        chunk_name = self._transform_row_to_lines(err_name, width)
        chunk_threat = self._transform_row_to_lines(err_threat, width)
        chunk_message = self._transform_row_to_lines(err_message, width)
        chunk_tips = self._transform_row_to_lines(err_tips, width)

        return [*chunk_name, *chunk_threat], [*chunk_message, *chunk_tips]

    def _create_body(self, width):
        """Create the body block of the error message window.

        Args:
            width (int): The width of the error message window.

        Returns:
            list[str]: the printable lines of the body.
        """
        first_lines, second_lines = self._build_body_sections(width)
        first_block = self._add_border(first_lines)
        second_block = self._add_border(second_lines)
        blank_line = self._create_blank_line(width)
        return [*first_block, blank_line, *second_block]

    def _construct_error_window(self, width):
        """Construct the complete error window.

        Args:
            width (int): The width of the error message window.

        Returns:
            list[str]: The printable lines of the error.
        """
        message_to_print = []

        header = self._create_header(width)
        message_to_print.extend(header)

        body = self._create_body(width)
        message_to_print.extend(body)

        footer = self._create_footer(width)
        message_to_print.extend(footer)

        return message_to_print

    def display_error(self):
        """Create and print the error window."""
        width = self._calculate_width()
        message_to_print = self._construct_error_window(width)
        for line in message_to_print:
            self.display_func(line)
