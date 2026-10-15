import pytest


@pytest.mark.xray('SYN-1')
@pytest.mark.parametrize('value', [0, 1], ids=['first-fails', 'last-passes'])
def test_parameter(value):
    assert value == 1
