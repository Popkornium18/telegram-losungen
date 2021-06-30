"""Functions for importing Losungen from the official download page"""
from zipfile import ZipFile
import datetime
import xml.etree.ElementTree as ET
import os
import re
import requests
from losungen import Session
from losungen.models import TagesLosung

LOSUNGEN_URL = "https://www.losungen.de/fileadmin/media-losungen/download"
LOSUNGEN_XML = "losungen.xml"


def download_zip(year):
    """Downloads the zipped XML file containing the Losungen of the given year"""
    url = f"{LOSUNGEN_URL}/Losung_{year}_XML.zip"
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 404:
            return False
    except requests.exceptions.RequestException as exc:
        print(f"Unable to download {url}")
        print(exc)
        return False
    open(f"{LOSUNGEN_XML}.zip", "wb").write(response.content)
    return True


def extract_zip(filename=f"{LOSUNGEN_XML}.zip"):
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


def import_xml(filename=LOSUNGEN_XML):
    """Imports all Losungen contained in the given XML file"""
    tree = ET.parse(LOSUNGEN_XML)
    os.remove(filename)
    root = tree.getroot()
    session = Session()
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
        session.add(
            TagesLosung(
                date=date,
                special_date=special_date_short,
                losung=losung,
                losung_verse=losung_verse,
                lehrtext=lehrtext,
                lehrtext_verse=lehrtext_verse,
            )
        )
    session.commit()


def import_year(year=datetime.date.today().year + 1):
    """Downloads, extracts and imports the Losungen"""
    if download_zip(year):
        extract_zip()
        import_xml()
        print(f"Successfully imported Losungen for {year}")
        return True

    print(f"Failed to download zip archive for {year}")
    return False


def initial_import():
    """Imports all available zip archives from the Losungen download page"""
    year = datetime.date.today().year
    year_iter = year
    while import_year(year_iter):
        year_iter -= 1

    year_iter = year + 1
    while import_year(year_iter):
        year_iter += 1
