import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import isbnlib
from lxml import etree
from pytz import UTC

from ..import_base import ImportBase, ImporterRecord, DataImportError, DataFormat

log = logging.getLogger(__name__)


class ImportOnixBase(ImportBase):
    SCHEMA_FILE = None
    TYPE_NAME = None
    NS = None

    # Map of ONIX identifier codes to Themis names
    IDENTIFIER_TYPE_MAP = {
        "02": "ISBN10",
        "03": "GTIN13",
        "04": "UPC",
        "06": "DOI",
        "15": "ISBN13",
        "23": "OCLC",
    }

    def __init__(self, filename_or_stream, close_file=None, validate=True):
        """
        An iterative reader of Products from an ONIX XML.

        Use a subclass for Onix 3.0 or 2.1. Iterates over:

        * XML documents with a single Product (`next_product_document`), or
        * `ThemisRecord`s (`next_themis_record()`).

        In both cases, the XML record for Product is the entire XML: a document with
        one Header and one Product, duplicating the header data for completeness.
        Validates the XML against a schema by default.

        By default, closes files given as filenames, and leaves streams open.
        """
        super().__init__(filename_or_stream, close_file)

        if validate and self.SCHEMA_FILE:
            schema_dir = Path(__file__).resolve().parent / 'data'
            schema_path = schema_dir / self.SCHEMA_FILE
            self.schema = etree.XMLSchema(file=str(schema_path))
        else:
            self.schema = None

        # Root <ONIXMessage> Element
        self.root_tag = None
        # The ONIX <header> element, read when encountered
        self.header = None
        # Iterator over ended header and product elements of the XML
        self.iterparser = etree.iterparse(
            self.file,
            tag=("{*}Header", "{*}Product", "{*}ONIXMessage"),
            schema=self.schema,
            events=("start", "end"),
        )
        self.product_counter = 0

    def __iter__(self):
        return self

    def __next__(self) -> ImporterRecord:
        """
        Returns the next ImporterRecord
        """
        root, el = self.next_product_document()
        if el is None:
            raise StopIteration

        return ImporterRecord(
            self.get_ssid(el),
            isbn=self.get_isbn(el),
            doi=self.get_doi(el),
            title=self.get_title(el),
            raw_data=etree.tostring(root, encoding="utf-8"),
            raw_data_format=DataFormat.XML,
            identifiers=self.get_identifiers(el),
            timestamp=self.get_timestamp(root),
        )

    def next_product_document(self):
        """
        Returns a pair of Elements `(root, product)` for the next Product, or `(None, None)`.

        The `root` is the full ONIX XML tree with the header and exactly one Product,
        which is returned as well as `product` for convenience.

        NB: The returned `root` is valid only until the next call to this method
        and is internally modified afterwards.
        """
        while True:
            try:
                event, el = next(self.iterparser)
            except StopIteration:
                return (None, None)
            if re.match("(.*})?ONIXMessage$", el.tag) and event == "start":
                assert self.root_tag is None
                self.root_tag = el.tag
            elif re.match("(.*})?Header$", el.tag) and event == "end":
                assert self.header is None
                self.header = el
            elif re.match("(.*})?Product$", el.tag) and event == "end":
                assert self.header is not None
                root_el = etree.Element(self.root_tag)
                root_el.append(self.header)
                root_el.append(el)
                self.product_counter += 1
                return root_el, el

    def get_specific_properties(self, element):
        raise NotImplementedError

    def get_identifiers(self, element) -> Dict[str, str]:
        """
        Get book identifiers - variant with namespaces.
        """
        ids = {}
        for id_el in self.xpath(element, "ProductIdentifier"):
            t = self.xpath(id_el, "ProductIDType")[0].text.strip()
            val = self.xpath(id_el, "IDValue")[0].text.strip()
            if t in self.IDENTIFIER_TYPE_MAP:
                ids[self.IDENTIFIER_TYPE_MAP[t]] = val
        return ids

    def get_ssid(self, element) -> str:
        """
        Returns a 'source specific id' - ID under which this record is stored in the source
        """
        raise NotImplementedError

    def get_isbn(self, element) -> Optional[str]:
        """
        Returns normalized ISBN13 from whatever source there is in the data
        """
        raise NotImplementedError

    def get_doi(self, element) -> Optional[str]:
        """
        If DOI of the work is available, returns it.
        """
        raise NotImplementedError

    def get_title(self, element) -> Optional[str]:
        """
        Returns clean (markup free) title of the work
        """
        raise NotImplementedError

    def get_timestamp(self, element) -> Optional[datetime]:
        """
        Returns timestamp of the record as present in the data
        """
        raise NotImplementedError

    @classmethod
    def xpath(cls, el, q):
        if cls.NS is not None:
            return el.xpath(f"o:{q}", namespaces={"o": cls.NS})
        else:
            return el.xpath(f"{q}")


# class ImportOnix30Reference(ImportOnixBase):
#     SCHEMA_FILE = "onix/v3.0/ONIX_BookProduct_3.0_reference.xsd"
#     TYPE_NAME = "onix30reference"
#     NS = "http://ns.editeur.org/onix/3.0/reference"


class ImportOnix21Reference(ImportOnixBase):
    # Note: the v2.1 XML files are not tagged with a namespace, breaking validation
    SCHEMA_FILE = None
    SCHEMA_FILE_UNUSED = "onix/v2.1/ONIX_BookProduct_Release2.1_reference.xsd"
    TYPE_NAME = "onix21reference"
    NS = None
    NS_UNUSED = "http://www.editeur.org/onix/2.1/reference"

    def get_specific_properties(self, element):
        title_els = element.xpath("Title/TitleText")
        return {
            "onix_sent_date": datetime.strptime(
                self.message_root.xpath("Header/SentDate")[0].text.strip(), "%Y%m%d%H%M%S"
            ),
            "onix_record_reference": element.xpath("RecordReference")[0].text.strip(),
            "onix_notification_type": element.xpath("NotificationType")[0].text.strip(),
            "title": title_els[0].text.strip() if title_els else None,
        }

    def get_ssid(self, element):
        for ref in self.xpath(element, 'RecordReference'):
            return ref.text.strip()
        raise DataImportError('ssid (RecordReference) not found in the source data')

    def get_title(self, element) -> Optional[str]:
        for title_el in element.xpath("Title"):
            title_type = title_el.xpath('TitleType')
            if title_type and title_type[0].text.strip() == '01':
                title_text = title_el.xpath('TitleText')
                return title_text[0].text.strip() if title_text else None

    def get_isbn(self, element) -> str:
        """
        Returns normalized ISBN13 from whatever source there is in the data
        """
        identifiers = self.get_identifiers(element)
        isbn = identifiers.get('ISBN13', identifiers.get('ISBN10'))
        if isbn and (isbnlib.is_isbn10(isbn) or isbnlib.is_isbn13(isbn)):
            isbn13 = isbnlib.canonical(isbnlib.to_isbn13(isbn))
            return isbn13

    def get_doi(self, element) -> Optional[str]:
        identifiers = self.get_identifiers(element)
        return identifiers.get('DOI')

    def get_timestamp(self, element) -> Optional[datetime]:
        date = datetime.strptime(element.xpath("Header/SentDate")[0].text.strip(), "%Y%m%d%H%M%S")
        return date.replace(tzinfo=UTC)
