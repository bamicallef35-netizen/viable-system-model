from vsm.cli import demo, main


def test_demo_is_deterministic() -> None:
    assert demo() == demo()


def test_demo_covers_every_section() -> None:
    out = demo()
    assert "THE RECURSION" in out
    assert "Company  [S2 S3 S3* S4 S5]" in out
    assert "structurally viable: yes" in out
    assert "REQUISITE VARIETY" in out
    assert "Plant South" in out and "NO " in out            # the short plant is flagged
    assert "VARIETY ENGINEERING" in out
    assert "ALGEDONIC  t=4  line-S2" in out
    assert "via Plant South -> Company" in out
    assert "!S4" in out                                      # the broken plant's missing function
    assert "structurally viable: no" in out


def test_main_demo_returns_zero(capsys: object) -> None:
    assert main(["demo"]) == 0


def test_main_usage_on_bad_args() -> None:
    assert main(["bogus"]) == 2
