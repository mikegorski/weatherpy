from weatherpy import __version__


def test_version_should_be_proper_number_and_format():
    assert __version__ == "0.1.0"
