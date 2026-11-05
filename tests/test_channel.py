import pytest

from vsm import Channel, channel_violations


def test_channel_rejects_negative_capacity() -> None:
    with pytest.raises(ValueError):
        Channel(-1)


def test_transmission_saturates_only_above_capacity() -> None:
    ch = Channel(4)
    assert not ch.transmit(3).saturated
    assert not ch.transmit(4).saturated
    over = ch.transmit(5.5)
    assert over.saturated and over.lost_bits == 1.5


def test_sound_plumbing_has_no_violations() -> None:
    assert channel_violations(served_variety_bits=5, channel_capacity_bits=6, transducer_variety_bits=6) == []


def test_undersized_channel_is_flagged() -> None:
    problems = channel_violations(served_variety_bits=7, channel_capacity_bits=6, transducer_variety_bits=8)
    assert len(problems) == 1 and "channel capacity" in problems[0]


def test_undersized_transducer_is_flagged() -> None:
    problems = channel_violations(served_variety_bits=5, channel_capacity_bits=6, transducer_variety_bits=5)
    assert len(problems) == 1 and "transducer" in problems[0]


def test_both_violations_are_reported() -> None:
    assert len(channel_violations(7, 6, 5)) == 2
