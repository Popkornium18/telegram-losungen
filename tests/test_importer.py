"""Tests for the importer"""
import datetime
import os
from importer import download_zip, extract_zip, _load_xml, LOSUNGEN_XML


def test_download_losungen():
    """Tests downloading the zip archive of this years losungen,
    extraction of the xml and loading of the losungen objects"""
    year = datetime.date.today().year
    zipfile = f"{LOSUNGEN_XML}.zip"

    assert download_zip(year)
    assert os.path.isfile(zipfile)
    extract_zip()
    assert not os.path.isfile(zipfile)
    assert os.path.isfile(LOSUNGEN_XML)
    losungen = _load_xml(LOSUNGEN_XML)
    assert not os.path.isfile(LOSUNGEN_XML)
    assert len(losungen) == 365
