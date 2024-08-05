import pytest
from django.core.management import call_command

from bookrank.models import WorkSet, WorkCategory, Work
from aleph.models import AlephEntry


ALEPH_ENTRY_DATA = [
    {
        "uid": "018221798",
        "raw_data": {
            "cat": [
                {"2": "psh", "7": "psh11052", "a": "osobní automobily", "x": "sr"},
                {"2": "psh", "7": "psh11056", "a": "historické automobily", "x": "sr"},
                {"2": "psh", "7": "psh8015", "a": "konstrukce", "x": "ob"},
                {"2": "psh", "7": "psh13733", "a": "jízdní vlastnosti", "x": "sr"},
                {"2": "psh", "7": "psh5132", "a": "historie vědy a techniky", "x": "hi"},
                {"2": "psh", "7": "psh5042", "a": "historie", "x": "hi"},
            ],
            "udc": [{"2": "MRF", "a": "629.331(091)"}, {"2": "MRF", "a": "629.021"}],
            "lang": "cze",
            "title": [{"a": "Aerodynamická senzace :", "b": "Tatra 77 /", "c": "Jan Tuček"}],
            "author": [{"4": "aut", "7": "jk01140318", "a": "Tuček, Jan,", "d": "1953-"}],
        },
    },
    {
        "uid": "018221800",
        "raw_data": {
            "cat": [
                {"2": "psh", "7": "psh12261", "a": "vojenská technika", "x": "vv"},
                {"2": "psh", "7": "psh13655", "a": "stíhací letadla", "x": "sr"},
                {"2": "psh", "7": "psh11154", "a": "letadlové systémy", "x": "sr"},
                {"2": "psh", "7": "psh3449", "a": "optické přístroje", "x": "fy"},
                {"2": "psh", "7": "psh1781", "a": "elektronika", "x": "el"},
            ],
            "udc": [
                {"2": "MRF", "a": "623.74(437.3)"},
                {"2": "MRF", "a": "623.4.05"},
                {"2": "MRF", "a": "623.4.052.5"},
                {"2": "MRF", "a": "621.38"},
            ],
            "lang": "cze",
            "title": [{"a": "Litening 4i pro české Gripeny /", "c": "Tomáš Soušek"}],
            "author": [{"4": "aut", "7": "mzk2006348548", "a": "Soušek, Tomáš,", "d": "1977-"}],
        },
    },
    {
        "uid": "018221787",
        "raw_data": {
            "cat": [
                {"2": "psh", "7": "psh11139", "a": "vojenská letadla", "x": "sr"},
                {"2": "psh", "7": "psh11142", "a": "konstrukce letadel", "x": "sr"},
                {"2": "psh", "7": "psh11165", "a": "letové zkoušky", "x": "sr"},
                {"2": "psh", "7": "psh8092", "a": "vývoj", "x": "ob"},
            ],
            "udc": [
                {"2": "MRF", "a": "623.746.7(437.312)"},
                {"2": "MRF", "a": "629.746.7"},
                {"2": "MRF", "a": "533.6.054"},
            ],
            "lang": "cze",
            "title": [{"a": "Aero L-39NG se připravuje ke vzletu"}],
        },
    },
]


@pytest.fixture()
def aleph_entries():
    return [AlephEntry.objects.create(**record) for record in ALEPH_ENTRY_DATA]
