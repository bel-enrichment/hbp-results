# -*- coding: utf-8 -*-

"""This script converts the curation sheets to BEL."""

import os

import bel_enrichment.sheets
from pybel import BELGraph

AUTHORS = [
    'Charles Tapley Hoyt',
    'Daniel Domingo-Fernández',
    'Esther Wollert',
    'Sandra Spalek',
    'Keerthika Lohanadan',
    'Rana Al Disi',
    'Lingling Xu',
    'Kristian Kolpeja',
]

AUTHOR_STRING = ', '.join(sorted(AUTHORS, key=lambda s: s.split()[-1]))

# Folder pointers
HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIRECTORY = os.path.abspath(os.path.join(HERE, os.pardir, 'rounds'))

CACHE_DIRECTORY = os.path.abspath(os.path.join(HERE, os.pardir, 'cache'))
os.makedirs(CACHE_DIRECTORY, exist_ok=True)

SHEETS_BEL_CACHE_PATH = os.path.join(CACHE_DIRECTORY, 'sheets.bel.pickle')


def get_sheets_graph(use_cached: bool = False) -> BELGraph:
    """Get the BEL graph from all Google sheets.

    .. warning:: this BEL graph isn't pre-filled with namespace and annotation URLs
    """
    graph_metadata = dict(
        name='HBP - INDRA Curation',
        version='0.1.0',
        authors=AUTHOR_STRING,
        contact='charles.hoyt@scai.fraunhofer.de',
    )

    return bel_enrichment.sheets.get_sheets_graph(
        directory=DATA_DIRECTORY,
        use_cached=use_cached,
        cache_path=SHEETS_BEL_CACHE_PATH,
        **graph_metadata,
    )


def generate_curation_summary():
    """Generate a summary of the curation results on excel."""
    return bel_enrichment.sheets.generate_curation_summary(
        input_directory=DATA_DIRECTORY,
        output_directory=CACHE_DIRECTORY,
    )


if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    logger.info('Creating INDRA curation report')
    generate_curation_summary()

    logger.info('Summarizing content')
    graph = get_sheets_graph()
    graph.summarize()
