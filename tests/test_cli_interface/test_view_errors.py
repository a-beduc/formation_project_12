"""Unit tests for ee_crm.cli_interface.views.view_errors"""
import pytest

from ee_crm.cli_interface.views.view_errors import ErrorView


@pytest.fixture
def fake_error_factory():
    def factory(threat="error", level='test', tips='default tip', msg=None):
        class FakeException(Exception):
            pass
        FakeException.threat = threat
        FakeException.level = level
        FakeException.tips = tips
        return ErrorView(FakeException(msg))
    return factory


@pytest.mark.parametrize(
    'value, expected',
    [
        ("error", ErrorView.error),
        ("warning", ErrorView.warning),
        ("other", ErrorView.echo)
    ]
)
def test_set_display_func(fake_error_factory, value, expected):
    view = fake_error_factory(threat=value)
    view.set_display_func(value)
    assert view.display_func == expected


@pytest.mark.parametrize(
    'terminal_width, expected',
    [
        (50, 50),
        (80, 64)
    ]
)
def test_calculate_width(mocker, fake_error_factory, terminal_width, expected):
    mocker.patch("ee_crm.cli_interface.views.view_errors.get_terminal_size",
                 return_value=mocker.Mock(columns=terminal_width))
    view = fake_error_factory()
    width = view._calculate_width()

    assert expected == width


def test_create_blank_line(fake_error_factory):
    view = fake_error_factory()
    view.delimitation = "▓"
    blank_line = view._create_blank_line(width=10)

    expected = "▓▓      ▓▓"

    assert expected == blank_line


def test_create_header(fake_error_factory):
    view = fake_error_factory()
    view.delimitation = "▓"
    header_block = view._create_header(width=20)

    expected = (
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓▓▓▓ E R R O R ▓▓▓▓▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓▓                ▓▓"
    )

    assert expected == header_block


def test_create_footer(fake_error_factory):
    view = fake_error_factory()
    view.delimitation = "▓"
    footer_block = view._create_footer(width=20)

    expected = (
        "▓▓                ▓▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
    )

    assert expected == footer_block


@pytest.mark.parametrize(
    "side, expected",
    [
        ("left", "▓▓ "),
        ("right", " ▓▓")
    ]
)
def test_create_border(fake_error_factory, side, expected):
    view = fake_error_factory()
    view.delimitation = "▓"
    border = view._create_border(side=side)

    assert border == expected


def test_transform_text_to_chunks():
    text = "This is the error message that will split."
    width = 16
    chunks = ErrorView._transform_text_to_chunks(text, width)

    expected = [
        'This is th',
        'e error me',
        'ssage that',
        ' will spli',
        't.',
    ]

    assert expected == chunks


@pytest.mark.parametrize(
    "chunks, expected",
    [
        (["this is a 20e chunk.", "2e chunk"],
         ["this is a 20e chunk.", "2e chunk      "]),
        (["this is a 20e chunk.", "second one is 20 too"],
         ["this is a 20e chunk.", "second one is 20 too"])
    ]
)
def test_fill_last_chunks(chunks, expected):
    new_chunks = ErrorView._fill_last_chunks(chunks, 20)

    assert expected == new_chunks


def test_transform_row_to_lines(fake_error_factory):
    text = "This is the error message that will split."
    width = 16
    view = fake_error_factory()
    chunks = view._transform_row_to_lines(text, width)

    expected = [
        'This is th',
        'e error me',
        'ssage that',
        ' will spli',
        't.        ',
    ]

    assert expected == chunks


def test_add_border(fake_error_factory):
    view = fake_error_factory()
    lines = ["this is a line", "this is a second line", "this is a third line"]
    bordered_lines = view._add_border(lines)

    expected = [
        '▓▓ this is a line ▓▓',
        '▓▓ this is a second line ▓▓',
        '▓▓ this is a third line ▓▓',
    ]

    assert expected == bordered_lines


def test_build_body_section(fake_error_factory):
    view = fake_error_factory(msg="this is the message part.")
    width = 20

    body_block = view._build_body_sections(width)

    expected = (
        [
            'Error name : F',
            'akeException  ',
            'Error at the t',
            'est level     ',
        ],
        [
            'Message : this',
            ' is the messag',
            'e part.       ',
            'Tips : default',
            ' tip          ',
        ],
    )

    assert expected == body_block


def test_build_body_sections(fake_error_factory):
    view = fake_error_factory(msg="this is the message part.")
    width = 20

    body_block = view._create_body(width)

    expected = [
        '▓▓ Error name : F ▓▓',
        '▓▓ akeException   ▓▓',
        '▓▓ Error at the t ▓▓',
        '▓▓ est level      ▓▓',
        '▓▓                ▓▓',
        '▓▓ Message : this ▓▓',
        '▓▓  is the messag ▓▓',
        '▓▓ e part.        ▓▓',
        '▓▓ Tips : default ▓▓',
        '▓▓  tip           ▓▓',
    ]

    assert expected == body_block


def test_construct_error_window(mocker, fake_error_factory):
    view = fake_error_factory(msg="this is the message part.")
    width = 20

    error_window = view._construct_error_window(width)

    expected = [
        '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
        '▓▓▓▓ E R R O R ▓▓▓▓▓',
        '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
        '▓▓                ▓▓',
        '▓▓ Error name : F ▓▓',
        '▓▓ akeException   ▓▓',
        '▓▓ Error at the t ▓▓',
        '▓▓ est level      ▓▓',
        '▓▓                ▓▓',
        '▓▓ Message : this ▓▓',
        '▓▓  is the messag ▓▓',
        '▓▓ e part.        ▓▓',
        '▓▓ Tips : default ▓▓',
        '▓▓  tip           ▓▓',
        '▓▓                ▓▓',
        '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
    ]

    assert expected == error_window
