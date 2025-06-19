import click


class BaseView:
    @staticmethod
    def echo(text, nl=True):
        click.echo(text, nl=nl)

    @classmethod
    def success(cls, msg, nl=True):
        cls.echo(click.style(msg, fg='green'), nl=nl)

    @classmethod
    def error(cls, msg, nl=True):
        cls.echo(click.style(msg, fg='bright_red'), nl=nl)

    @classmethod
    def warning(cls, msg, nl=True):
        cls.echo(click.style(msg, fg='bright_yellow'), nl=nl)
