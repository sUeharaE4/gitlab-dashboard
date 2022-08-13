from common import util


def test_flatten_dict_in_dict():
    nest = {
        "no-change": "no-change-value",
        "author": {
            "id": 1,
            "name": "name"
        }
    }
    expect = {
        "no-change": "no-change-value",
        "author-id": 1,
        "author-name": "name"
    }
    util.flatten_dict_in_dict(nest)
    assert nest == expect


def test_len_nullable_list():
    assert util.len_nullable_list(None) == 0
    assert util.len_nullable_list([]) == 0
    assert util.len_nullable_list(()) == 0
    assert util.len_nullable_list([i for i in range(3)]) == 3
