# -*- coding: UTF-8 -*-
from enum import IntEnum


class ScrapeStatusEnum(IntEnum):
    interrupted = 0
    success = 1

    db_multiple_search_results = 2
    db_not_found = 3

    library_multiple_search_results = 4
    library_not_found = 5

    bus_multiple_search_results = 6
    bus_not_found = 7

    arzon_exist_but_no_plot = 8
    arzon_not_found = 9


class CompletionStatusEnum(IntEnum):
    unknown = 0

    only_db = 1,
    only_library = 2
    only_bus = 3

    db_library = 4
    db_bus = 5
    db_library_bus = 6

    library_bus = 7


class CutTypeEnum(IntEnum):
    unknown = 0
    left = 1
    middle = 2
    right = 3
    custom = 4
