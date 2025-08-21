"""Implementation of a class that mainly transform list of object into
printable tables.

Main interface is through the CrudView.render method.

Classes:
    CrudView    # Data manipulation to present information to terminal.
"""
from shutil import get_terminal_size

from ee_crm.cli_interface.views.view_base import BaseView


class CrudView(BaseView):
    """View class for displaying list of object in a table.

    Inherits from BaseView, which implement print-like functions with
    Click.

    Attributes (class):
        label: Used for the title and identification of the table.
        columns: Ordered columns name.
        weight_width_allocation: Mapping between columns name and
            relative allocated width.
        max_width_allocation: Mapping between columns name and
            maximum allocated width.
        separator: Mapping between keyword-name and separator character.

    Attributes (instance):
        allocated_width: Calculated value mapped between columns name
            and actual width. May be empty.
        instance_columns: Effective columns names requested.
        sum_weight: Cache to avoid multiple calculations of instance
            columns weight.

    Interface:
        render(data, remove_col=None): Method used to process data.
    """
    label: str
    columns: list[str]
    weight_width_allocation: dict[str, int]
    max_width_allocation: dict[str, int]

    # Not be the best naming for keywords.
    # d : double / c : corner or cross / t : top / l : left or line /
    # r : right / b : bottom / v : vertical / h : horizontal
    separator = {
        "dctl": "╔",
        "dctr": "╗",
        "dcbl": "╚",
        "dcbr": "╝",
        "dlv": "║",
        "dlh": "═",
        "lh": "─",
        "lv": "│",
        "lc": "┼"
    }

    def __init__(self):
        self.allocated_width = {}
        self.instance_columns = list(self.columns)
        self.sum_weight = None

    @staticmethod
    def _prepare_chunks(text, size):
        """Split a text into a list of chunks.

        Args:
            text (str): The text to be split.
            size (int): The size of the chunks.

        Returns:
            list[str]: The chunks.
        """
        if text is None:
            return ['']
        text = str(text)
        return [text[i:i+size] for i in range(0, len(text), size)]

    def _prepare_header(self):
        """Associate columns to list of string to create header lines.

        Multiple lines for a columns header may happen if table is too
        narrow.

        Returns:
            dict[list]: The header lines with the columns name as key.
        """
        return {
            col: self._prepare_chunks(col, self.allocated_width[col])
            for col in self.instance_columns
        }

    def _prepare_object(self, obj_dto):
        """Associate object value to list of string to create the body
        lines.

        Args:
            obj_dto (Object): The dataclass object than contains the
                information.

        Returns:
            dict[list]: The body lines with the columns name as key.
        """
        return {
            col: self._prepare_chunks(getattr(obj_dto, col),
                                      self.allocated_width[col])
            for col in self.instance_columns
        }

    def _make_separator(self):
        """Create the separator line.

        Returns:
            str: The separator line as a string.
        """
        col_chunk = [
            self.separator['lh'] * self.allocated_width[col]
            for col in self.instance_columns
        ]
        return (f"{self.separator['dlv']}"
                f" {self.separator['lc'].join(col_chunk)} "
                f"{self.separator['dlv']}")

    def _calculate_col_width(self, col_key, available_width):
        """Calculate a column width.

        Choose the minimum value between the max possible for the column
        and the available width. The width allocation for the column is
        dependent on the weight of the column.

        Args:
            col_key (str): The column name.
            available_width (int): The available width.

        Returns:
            int: The column width.
        """
        max_alloc = self.max_width_allocation[col_key]

        # cache sum of all weights
        if not self.sum_weight:
            list_of_weights = [w
                               for k, w in self.weight_width_allocation.items()
                               if k in self.instance_columns]
            self.sum_weight = sum(list_of_weights)

        dyn_alloc = int(self.weight_width_allocation[col_key] *
                        available_width / self.sum_weight)
        return min(max_alloc, dyn_alloc)

    def _spread_extra_space(self, available_width):
        """Redistribute space that was not properly distributed (due to
        approximation).
        It does the redistributions incrementally so that if a column
        reach its maximum, it is pruned from the pool of candidates.
        If all columns have reached their maximum or no more space to
        distribute, break.

        Args:
            available_width (int): The total available width.
        """
        extra = available_width - sum(self.allocated_width.values())
        if extra <= 0:
            return

        candidates = [c for c in self.instance_columns
                      if self.allocated_width[c] <
                      self.max_width_allocation[c]]

        while extra and candidates:
            for col in list(candidates):
                self.allocated_width[col] += 1

                extra -= 1
                if extra == 0:
                    break

                if self.allocated_width[col] >= self.max_width_allocation[col]:
                    candidates.remove(col)

    def _calculate_table_and_col_width(self):
        """Calculate width of elements based on available width and weight of
        columns. If space wasn't used it can be redistributed to columns that
        have not reached their cap.

        Due to Windows PowserShell, a space is left unused at the end of
        every line to avoid auto-wrapper shenanigans.

        Returns:
            Int: The table width.
        """
        width = get_terminal_size().columns
        left_padding, right_padding = 2, 2
        padding = left_padding + right_padding
        separators = len(self.instance_columns) - 1
        # -1 to avoid PowserShell auto-wrapper
        available_width = width - padding - separators - 1

        self.allocated_width = \
            {k: self._calculate_col_width(k, available_width)
             for k in self.instance_columns}

        self._spread_extra_space(available_width)

        # Reset cache
        self.weight = None

        # Width of table elements
        columns = sum(self.allocated_width.values())
        padding = 4
        separators = len(self.instance_columns) - 1

        return columns + padding + separators

    def _construct_top_line(self, table_width):
        """Create the top line of the table.

        Args:
            table_width (int): The table width.

        Returns:
            str: The string representing the top line.
        """
        table_label = f" {self.label} Table "
        width_label = len(table_label)
        width_line = (table_width - 2 - width_label) // 2
        width_leftover = (table_width - 2 - width_label) % 2
        width_line_left = width_line
        width_line_right = width_line + width_leftover
        return (f"{self.separator['dctl']}"
                f"{width_line_left * self.separator['dlh']}"
                f"{table_label}"
                f"{width_line_right * self.separator['dlh']}"
                f"{self.separator['dctr']}")

    def _transform_row_to_lines(self, cell_chunks):
        """Create string representing a formatted line of the table.
        It uses the index of the list of string to aggregate the content
        per line.
        It means, cell one first element (index 0) is added to a string,
        then we add separator, then cell two first element (index 0),
        then a separator etc...
        When all the element of the dict have used their index 0, it
        repeats for the next indexes.

        Args:
            cell_chunks (dict): A dictionary that maps column names to
                a list of strings (content of a cell).

        Returns:
            list[str]: A list of printable lines.
        """
        height = max(len(ch) for ch in cell_chunks.values())

        lines = []
        for index in range(height):
            parts = []
            for col in self.instance_columns:
                # if no chunk for current index, add empty chunk.
                chunk = cell_chunks[col][index] \
                    if index < len(cell_chunks[col]) \
                    else ''

                # if chunk is not long enough, add blank.
                norm_chunk = chunk.ljust(self.allocated_width[col])
                parts.append(norm_chunk)

            line = (f"{self.separator['dlv']}"
                    f" {self.separator['lv'].join(parts)} "
                    f"{self.separator['dlv']}")
            lines.append(line)

        return lines

    def _create_table(self, data):
        """Create the table from a list of object.
        Each column of the table correspond to an attribute of the
        objects. Some attribute may not be used if they are not part of
        the instance columns (self.instance_columns).

        Args:
            data (list[Object]): A list of objects, ideally DTO.

        Returns:
            list[str]: A list of printable lines to display the content.
        """
        # calculate width
        table_width = self._calculate_table_and_col_width()

        lines = list()

        # top line
        lines.append(self._construct_top_line(table_width))

        # blank line
        blank_line = (f"{self.separator['dlv']}"
                      f"{(table_width - 2) * ' '}"
                      f"{self.separator['dlv']}")
        lines.append(blank_line)

        # headers line
        header_chunk = self._prepare_header()
        for line in self._transform_row_to_lines(header_chunk):
            lines.append(line)

        # prepare separator line
        separator_line = self._make_separator()

        # add a separator after header
        lines.append(separator_line)

        # body
        for i, obj in enumerate(data):
            # obj lines
            obj_chunk = self._prepare_object(obj)
            obj_lines = self._transform_row_to_lines(obj_chunk)
            lines.extend(obj_lines)

            if i < len(data) - 1:
                # separator line
                lines.append(separator_line)

        # bot line
        lines.append(f"{self.separator['dcbl']}"
                     f"{(table_width - 2) * self.separator['dlh']}"
                     f"{self.separator['dcbr']}")

        return lines

    def _print(self, lines):
        """Print the lines.

        Args:
            lines (list[str]): A list of printable lines.
        """
        for line in lines:
            self.echo(line)

    def render(self, data, remove_col=None):
        """Interface to transform a list of object into a printed
        output.
        If no data is given, print a small error message.

        Args:
            data (list[Object]): A list of objects, ideally DTO.
            remove_col (list[str]): A list of column names to remove.
                It must be an iterable.
        """
        if not data:
            self.error(f"No {self.label.lower()} found.")
            return

        if remove_col is not None:
            for col in remove_col:
                if col in self.columns:
                    self.instance_columns.remove(col)

        lines = self._create_table(data)
        self._print(lines)
