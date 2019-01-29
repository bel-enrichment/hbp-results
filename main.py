# -*- coding: utf-8 -*-

"""This script converts the curation sheets to BEL."""

import os
import sys
from collections import Counter, defaultdict
from itertools import chain
from typing import Mapping

import click
import pandas as pd

import neurommsig_knowledge
from bel_enrichment import BELSheetsRepository
from pybel import BELGraph
from pybel.cli import echo_warnings_via_pager
from pybel.constants import ANNOTATIONS
from pybel.struct.grouping import get_subgraphs_by_annotation

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

ROUNDS_DIRECTORY = os.path.abspath(os.path.join(HERE, 'rounds'))
assert os.path.exists(ROUNDS_DIRECTORY)

DATA_DIRECTORY = os.path.abspath(os.path.join(HERE, 'data'))
os.makedirs(DATA_DIRECTORY, exist_ok=True)

graph_metadata = dict(
    name='HBP - INDRA Curation',
    version='0.1.0',
    authors=AUTHOR_STRING,
    contact='charles.hoyt@scai.fraunhofer.de',
)

sheets_repository = BELSheetsRepository(
    directory=ROUNDS_DIRECTORY,
    output_directory=DATA_DIRECTORY,
    metadata=graph_metadata,
)


def get_sheets_graph(use_cached: bool = True, use_tqdm: bool = True) -> BELGraph:
    """Get the BEL graph from all Google sheets.

    .. warning:: this BEL graph isn't pre-filled with namespace and annotation URLs
    """
    return sheets_repository.get_graph(use_cached=use_cached, use_tqdm=use_tqdm)


@click.command()
@click.option('-w', '--show-warnings', is_flag=True)
@click.option('-r', '--reload', is_flag=True)
def main(show_warnings: bool, reload: bool):
    sheets_repository.generate_curation_summary()

    graph = get_sheets_graph(use_cached=(not reload))
    graph.summarize()

    # summarize API
    indra_api_histogram = Counter(
        api
        for _, _, d in graph.edges(data=True)
        if ANNOTATIONS in d and 'INDRA_API' in d[ANNOTATIONS]
        for api in d[ANNOTATIONS]['INDRA_API']
        if api and isinstance(api, str) and api != 'nan'
    )
    click.echo('Readers Used:')
    api_size = max(len(api) for api in indra_api_histogram)
    for api, count in indra_api_histogram.most_common():
        click.echo(f'  {api:{api_size}}: {count}')
    indra_api_df = pd.DataFrame.from_dict(indra_api_histogram, orient='index')
    indra_api_df.to_csv(os.path.join(sheets_repository.output_directory, 'api_summary.tsv'), sep='\t')

    if graph.warnings:
        number_errored_documents = len({path for path, _, _ in graph.warnings})
        click.secho(f'Warnings from {number_errored_documents} documents')
        if show_warnings:
            echo_warnings_via_pager(graph.warnings)
            sys.exit(-1)

    # assign edges to subgraphs and report as table
    prior = neurommsig_knowledge.repository.get_graph()
    # get node to subgraph map
    node_to_subgraph = defaultdict(set)
    for u, v, d in prior.edges(data=True):
        subgraphs = set(d.get(ANNOTATIONS, {}).get('Subgraph', ()))
        node_to_subgraph[u].update(subgraphs)
        node_to_subgraph[v].update(subgraphs)

    prior_subgraphs = set(chain.from_iterable(node_to_subgraph.values()))

    for u, v, k, d in graph.edges(keys=True, data=True):
        annotations = d.get(ANNOTATIONS)
        if annotations is None:
            continue
        annotations['Subgraph'] = node_to_subgraph[u] | node_to_subgraph[v]

    combine_graph = prior + graph
    combine_graph.summarize()
    subgraphs: Mapping[str, BELGraph] = get_subgraphs_by_annotation(combine_graph, 'Subgraph')

    summary_df = pd.DataFrame.from_dict({
        name: subgraph.summary_dict()
        for name, subgraph in subgraphs.items()
        if name in prior_subgraphs
    }, orient='index')
    summary_df.to_csv(os.path.join(sheets_repository.output_directory, 'subgraph_summary.tsv'), sep='\t')


if __name__ == '__main__':
    main()
