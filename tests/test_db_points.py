"""Test points db."""
from src.server.db_points import getDB

DB = getDB("points")
CHNL = "__test__"


def flatten(batch_gen):
    """Flatten a generator of batches (lists) into a single list."""
    res = []
    for batch in batch_gen:
        res.extend(batch)
    return res


def test_all():

    DB.clear(CHNL)

    def as_update_item(number):
        return {
            "key": f'key_{str(number)}',
            "dim": number,
            "val": f'val_{str(number)}'
        }

    def as_remove_item(number):
        return {
            "key": f'key_{str(number)}'
        }

    update_items = [as_update_item(n) for n in range(10)]

    # update items
    DB.update(CHNL, update_items)

    # get items
    items = flatten(DB.get(CHNL))
    assert len(items) == 10

    # remove items
    remove_items = [as_remove_item(n) for n in range(5)]
    DB.update(CHNL, remove_items)

    # get items
    items = flatten(DB.get(CHNL))
    assert len(items) == 5

    # clear
    DB.clear(CHNL)

    # get items
    items = []
    for batch in DB.get(CHNL):
        items.extend(batch)
    assert len(items) == 0


def test_channels():
    """Test listing two channels."""
    CHNL_A = "A"
    CHNL_B = "B"
    DB.clear(CHNL_A)
    DB.clear(CHNL_B)
    ITEM = {"key": "key", "dim": 4, "val": "val"}
    DB.update(CHNL_A, ITEM)
    DB.update(CHNL_B, ITEM)
    res = DB.channels()
    assert CHNL_A in res
    assert CHNL_B in res
    DB.clear(CHNL_A)
    DB.clear(CHNL_B)


def test_lookup_remove():

    DB.clear(CHNL)

    # data
    items = [
        {"key": "A", "dim": 3, "val": "value A"},
        {"key": "B", "dim": 4, "val": "value B"},
        {"key": "C", "dim": 5, "val": "value C"},
        {"key": "D", "dim": 10, "val": "value D"},
        {"key": "E", "dim": 11, "val": "value E"},
    ]

    # insert
    DB.insert(CHNL, items)

    # clear
    itv_1 = (4, 10, False, False)
    # itv_2 = (4, 10, False, True)
    # itv_3 = (4, 10, True, False)
    # itv_4 = (4, 10, True, True)

    # remove search interval 1
    DB.update(CHNL, [{"cmd": "clear_range", "range": itv_1}])

    # get
    expect = set(["A", "B", "D", "E"])
    res = flatten(DB.get(CHNL))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0


def test_lookup():

    DB.clear(CHNL)

    # search intervals
    itv_1 = (4, 10, False, False)
    itv_2 = (4, 10, False, True)
    itv_3 = (4, 10, True, False)
    itv_4 = (4, 10, True, True)

    # data
    items = [
        {"key": "A", "dim": 3, "val": "value A"},
        {"key": "B", "dim": 4, "val": "value B"},
        {"key": "C", "dim": 5, "val": "value C"},
        {"key": "D", "dim": 10, "val": "value D"},
        {"key": "E", "dim": 11, "val": "value E"},
    ]

    # insert
    DB.insert(CHNL, items)

    # search interval 1
    expect = set(["C"])
    res = flatten(DB.lookup(CHNL, itv_1))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # search interval 2
    expect = set(["C", "D"])
    res = flatten(DB.lookup(CHNL, itv_2))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # search interval 3
    expect = set(["B", "C"])
    res = flatten(DB.lookup(CHNL, itv_3))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # search interval 1
    expect = set(["B", "C", "D"])
    res = flatten(DB.lookup(CHNL, itv_4))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # test unbounded left
    expect = set(["A", "B", "C", "D"])
    itv = (None, 10, True, True)
    res = next(DB.lookup(CHNL, itv))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # test unbounded right
    expect = set(["B", "C", "D", "E"])
    itv = (4, None, True, True)
    res = next(DB.lookup(CHNL, itv))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0

    # test unbounded both directions
    expect = set(["A", "B", "C", "D", "E"])
    itv = (None, None, True, True)
    res = next(DB.lookup(CHNL, itv))
    keys = set([cue["key"] for cue in res])
    failed = keys.difference(expect)
    missing = expect.difference(keys)
    assert len(expect) == len(res)
    assert len(failed) == 0
    assert len(missing) == 0
