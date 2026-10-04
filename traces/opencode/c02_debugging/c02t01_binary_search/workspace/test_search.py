from search import binary_search


def test_found_middle():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_found_first():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_found_last():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_absent():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1


def test_single_found():
    assert binary_search([42], 42) == 0


def test_single_absent():
    assert binary_search([42], 7) == -1


def test_two_elements():
    assert binary_search([1, 2], 2) == 1
