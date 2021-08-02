"""Functions for importing Losungen from the official download page"""
from typing import List
from zipfile import ZipFile
import datetime
import xml.etree.ElementTree as ET
import os
import re
import requests
import logging
from sqlalchemy.orm import Session
from losungen import SessionMaker
from losungen.models import TagesLosung
from losungen.repositories import TagesLosungRepository

LOSUNGEN_URL = "https://www.losungen.de/fileadmin/media-losungen/download"
LOSUNGEN_XML = "losungen.xml"

logger = logging.getLogger("telegram-losungen.importer")


def download_zip(year: int) -> bool:
    """Downloads the zipped XML file containing the Losungen of the given year"""
    url = f"{LOSUNGEN_URL}/Losung_{year}_XML.zip"
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 404:
            return False
        logger.info("Successfully downloaded %s", url)
    except requests.exceptions.RequestException as exc:
        logger.exception("Unable to download %s", url)
        return False
    open(f"{LOSUNGEN_XML}.zip", "wb").write(response.content)
    return True


def extract_zip(filename: str = f"{LOSUNGEN_XML}.zip") -> None:
    """Extracts the XML file from a Losungen zip file"""
    with ZipFile(filename) as zipfile:
        with open(LOSUNGEN_XML, "wb") as xmlfile:
            xmlfile.write(
                [
                    zipfile.read(file)
                    for file in zipfile.namelist()
                    if file.endswith(".xml")
                ][0]
            )
    os.remove(filename)
    logger.info("Successfully extracted %s", filename)


def _load_xml(filename: str) -> None:
    tree = ET.parse(LOSUNGEN_XML)
    os.remove(filename)
    root = tree.getroot()
    losungen: List[TagesLosung] = []
    for day in root:
        date_str = day.find("Datum").text
        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()
        special_date = day.find("Sonntag").text
        # Strip unnecessary text from special_date
        special_date_short = (
            special_date
            if special_date is None
            else re.sub(r" \(.*\)", "", str(special_date))
        )
        losung = day.find("Losungstext").text
        losung_verse = day.find("Losungsvers").text
        lehrtext_verse = day.find("Lehrtextvers").text
        lehrtext = day.find("Lehrtext").text
        tageslosung = TagesLosung(
            date=date,
            special_date=special_date_short,
            losung=losung,
            losung_verse=losung_verse,
            lehrtext=lehrtext,
            lehrtext_verse=lehrtext_verse,
        )
        losungen.append(tageslosung)

    return losungen


def import_xml(filename: str = LOSUNGEN_XML) -> None:
    """Imports all Losungen contained in the given XML file"""
    session: Session = SessionMaker()
    repo = TagesLosungRepository(session)
    for losung in _load_xml(filename):
        repo.add(losung)
    session.commit()


def import_year(year: int = None) -> bool:
    """Downloads, extracts and imports the Losungen of a given year.
    The year defaults to the next year."""
    session: Session = SessionMaker()
    repo = TagesLosungRepository(session)
    year = datetime.date.today().year + 1 if year is None else year
    losungen = repo.get_by_year(year)
    session.close()

    if losungen:
        return True  # Already imported

    if download_zip(year):
        extract_zip()
        import_xml()
        logger.info("Successfully imported Losungen for %i", year)
        return True

    logger.warning("Failed to download zip archive for %i", year)
    return False


def initial_import() -> None:
    """Imports all available zip archives from the Losungen download page"""
    year = datetime.date.today().year
    year_iter = year

    while import_year(year_iter):
        year_iter -= 1

    year_iter = year + 1
    while import_year(year_iter):
        year_iter += 1
