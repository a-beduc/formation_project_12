"""Class that implements methods to print message to the terminal
using the click module.

Classes:
    BaseView    # Simple class to implement methods for printing text.
"""
import click


class BaseView:
    """View class inherited to implement methods for printing text.
    It wraps click function so that it only to be imported in this
    module.
    """
    @staticmethod
    def echo(text, nl=True):
        """Wrap the click echo function."""
        click.echo(text, nl=nl)

    @classmethod
    def success(cls, msg, nl=True):
        """Color the success message. Green."""
        cls.echo(click.style(msg, fg='green'), nl=nl)

    @classmethod
    def error(cls, msg, nl=True):
        """Color the error message. Red."""
        cls.echo(click.style(msg, fg='bright_red'), nl=nl)

    @classmethod
    def warning(cls, msg, nl=True):
        """Color the warning message. Yellow."""
        cls.echo(click.style(msg, fg='bright_yellow'), nl=nl)
