import pytest

from bitrung import main


def test_main_says_hello(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    assert capsys.readouterr().out == "Hello from bitrung!\n"
