"""
Stuff related to working with data from SCKN - https://www.sckn.cz/
"""

from typing import Generator
import xml.etree.ElementTree as ElementTree
import logging
from urllib.request import urlopen

from ..lang import guess_language
from .abstract import CandidateImporter, CandidateRec

logger = logging.getLogger(__name__)


class SCKNImporter(CandidateImporter):

    LANG_TO_CODE = {'český': 'cze', 'anglický': 'eng', 'slovenský': 'slo', 'německý': 'ger'}
    ROLE_TO_CODE = {'Autor': 'aut', 'Překladatel': 'trl', 'Ilustrátor': 'ill', 'Editor': 'edt'}

    def gen_candidates(self, source: str) -> Generator[dict, None, None]:
        if source.startswith("https://"):
            doc = urlopen(source)
            try:
                tree = ElementTree.parse(doc)
            finally:
                doc.close()
        else:
            tree = ElementTree.parse(source)
        root = tree.getroot()
        for el in root:
            record = {}
            params = []
            contributors = []
            for child in el:
                if child.tag in (
                    'ITEM_ID',
                    'PRODUCTNAME',
                    'PRODUCT',
                    'EAN',
                    'ISBN',
                    'PRICE_VAT',
                    'PUBLISHER',
                    'DESCRIPTION',
                    'CATEGORYTEXT',
                    'URL',
                    'IMGURL',
                    'THEMATIC_GROUP',
                    'ISBN2',
                ):
                    assert len(child) == 0, "Only simple values allowed"
                    record[child.tag] = child.text
                elif child.tag == 'PARAM':
                    param = {}
                    for sub in child:
                        if sub.tag in ('PARAM_NAME', 'VAL'):
                            param[sub.tag] = sub.text
                        else:
                            logging.warning(
                                'Unexpected PARAM tag: %s (%d children)', sub.tag, len(sub)
                            )
                    params.append(param)
                elif child.tag == 'CONTRIBUTOR':
                    contributor = {}
                    for sub in child:
                        if sub.tag in ('ROLE', 'NAME', 'SURNAME'):
                            contributor[sub.tag] = sub.text
                        else:
                            logging.warning(
                                'Unexpected CONTRIBUTOR tag: %s (%d children)', sub.tag, len(sub)
                            )
                    contributors.append(contributor)
                else:
                    logger.warning('Unexpected tag: %s (%d children)', child.tag, len(child))
            record['params'] = params
            record['contributors'] = contributors
            yield record

    def raw_to_common(self, raw_data: dict) -> CandidateRec:
        id_in_source = raw_data.get('ITEM_ID', 'xxx')
        rec = CandidateRec(id_in_source)
        # title
        title = raw_data.get('PRODUCTNAME')
        if title != raw_data.get('PRODUCT'):
            logging.warning(
                "PRODUCTNAME differs from PRODUCT: '%s' X '%s'", title, raw_data.get('PRODUCT')
            )
        rec.title = title
        # params
        for param in raw_data['params']:
            if param['PARAM_NAME'] == 'Jazyk':
                lang = self.LANG_TO_CODE.get(param['VAL'], '')
                if not lang:
                    logger.warning("Unrecognized language: %s", param['VAL'])
                rec.lang = lang
        if not rec.lang:
            guess = guess_language(rec.title)
            if guess:
                rec.lang = guess
            else:
                logger.warning("Missing lang and could not guess: %s", rec.title)
                rec.lang = ''
        # contributors
        for cont in raw_data['contributors']:
            role = self.ROLE_TO_CODE.get(cont['ROLE'])
            if not role:
                logger.warning("Unrecognized role: %s", cont['ROLE'])
            rec.contributors.append(
                {'name': cont['NAME'], 'surname': cont['SURNAME'], 'role': role}
            )
        # other data
        publisher = raw_data.get('PUBLISHER')
        if publisher:
            rec.publisher = publisher
        isbn = raw_data.get('ISBN')
        if isbn:
            rec.isbn = isbn
        desc = raw_data.get('DESCRIPTION')
        if desc:
            rec.description = desc
        return rec
