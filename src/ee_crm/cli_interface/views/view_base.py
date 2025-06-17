from abc import ABC, abstractmethod
from shutil import get_terminal_size

import click


class BaseView(ABC):
    label: str
    columns: list[str]
    weight_width_allocation: dict[str, int]
    max_width_allocation: dict[str, int]
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

    @staticmethod
    def echo(text):
        click.echo(text)

    def _success(self, msg):
        self.echo(click.style(msg, fg='green'))

    def _error(self, msg):
        self.echo(click.style(msg, fg='red'))

    @staticmethod
    def _prepare_chunks(text, size):
        if text is None:
            return ['']
        text = str(text)
        return [text[i:i+size] for i in range(0, len(text), size)]

    def _prepare_header(self, row):
        return {
            col: self._prepare_chunks(row[col], self.allocated_width[col])
            for col in self.instance_columns
        }

    def _prepare_object(self, obj_dto):
        return {
            col: self._prepare_chunks(getattr(obj_dto, col),
                                      self.allocated_width[col])
            for col in self.instance_columns
        }

    def _make_separator(self):
        col_chunk = [
            self.separator['lh'] * self.allocated_width[col]
            for col in self.instance_columns
        ]
        return (self.separator['dlv'] + " " +
                self.separator['lc'].join(col_chunk) +
                " " + self.separator['dlv'])

    def _calculate_col_width(self, col_key, col_weight, available_width):
        max_alloc = self.max_width_allocation[col_key]
        sum_weight = sum([w for k, w in self.weight_width_allocation.items()
                          if k in self.instance_columns])
        dyn_alloc = int(col_weight * available_width / sum_weight)
        return min(max_alloc, dyn_alloc)

    def _spread_extra_space(self, available_width):
        extra = available_width - sum(self.allocated_width.values())
        if extra <= 0:
            return

        candidates = [c for c in self.instance_columns
                      if self.allocated_width[c] <
                      self.max_width_allocation[c]]

        while extra and candidates:
            for col in list(candidates):
                if self.allocated_width[col] < self.max_width_allocation[col]:
                    self.allocated_width[col] += 1
                    extra -= 1
                    if extra == 0:
                        break

                    if self.allocated_width[col] == self.max_width_allocation[col]:
                        candidates.remove(col)
                else:
                    candidates.remove(col)

    def _calculate_table_and_col_width(self):
        width = get_terminal_size().columns

        available_width = width - (4 + len(self.instance_columns) - 1)

        self.allocated_width = \
            {k: self._calculate_col_width(k, w, available_width)
             for k, w in self.weight_width_allocation.items()
             if k in self.instance_columns}

        self._spread_extra_space(available_width)

        return (sum(self.allocated_width.values())
                + 4 + len(self.instance_columns) - 1)

    def _construct_top_line(self, table_width):
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
        height = max(len(ch) for ch in cell_chunks.values())

        lines = []
        for h in range(height):
            parts = []
            for col in self.instance_columns:
                chunk = (
                    cell_chunks)[col][h] if h < len(cell_chunks[col]) else ''
                norm_chunk = chunk.ljust(self.allocated_width[col])
                parts.append(norm_chunk)
            line = (self.separator['dlv'] + " " +
                    self.separator['lv'].join(parts) +
                    " " + self.separator['dlv'])
            lines.append(line)

        return lines

    def _print(self, lines):
        for line in lines:
            self.echo(line)

    def render(self, data, remove_col=None):
        if not data:
            self._error(f"No {self.label.lower()} found.")
            return

        if remove_col is not None:
            for col in remove_col:
                if col in self.columns:
                    self.instance_columns.remove(col)

        # calculate width
        table_width = self._calculate_table_and_col_width()

        lines = list()

        # top line
        lines.append(self._construct_top_line(table_width))

        # blank line
        blank_line = (f"{self.separator['dlv']}"
                      f"{(table_width - 2) * " "}"
                      f"{self.separator['dlv']}")
        lines.append(blank_line)

        # headers line
        header_dict = {c: c for c in self.instance_columns}
        header_chunk = self._prepare_header(header_dict)
        for line in self._transform_row_to_lines(header_chunk):
            lines.append(line)

        # separator line
        lines.append(self._make_separator())

        # body
        for i, obj in enumerate(data):
            # obj lines
            obj_chunk = self._prepare_object(obj)
            obj_lines = self._transform_row_to_lines(obj_chunk)
            lines.extend(obj_lines)

            if i < len(data) - 1:
                # separator line
                lines.append(self._make_separator())

        # bot line
        lines.append(f"{self.separator['dcbl']}"
                     f"{(table_width - 2) * self.separator['dlh']}"
                     f"{self.separator['dcbr']}")

        self._print(lines)
