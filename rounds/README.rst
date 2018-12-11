Rational Enrichment with INDRA
==============================
This document describes an approach to enrich knowledge assemblies based on topological novelty.

1. Assemble BEL from relevant sources
-------------------------------------
1. Assemble BEL from relevant sources
2. Re-curate content with questionable quality
3. *Optional*: choose annotations that are relevant and filter the resulting network. We used the 
   "Subgraph" annotation from NeuroMMSig to select the ten most relevevant subgraphs to the MAVO 
   Project

2. Identitify Sad Nodes
-----------------------
Chemicals, biological processes, and pathologies are not considered since they are the logical inputs 
and outputs of a given mechanistic network. As a first step, they are removed from the network.

As a second step, all variants, proteins, RNAs, and miRNAs are collapsed to their corresponding genes.

Sad nodes are defined as nodes with a degree of 0 or 1 after this preprocessing step. They have been 
pre-determined to be interesting by inclusion int he knowledge assembly from Step 1.

3. Filter Sad Nodes
-------------------
Some of the sad nodes have already been quantified mechanistically, but just not in the given knowledge 
assembly. In this step, several sources (Pathway Comons, Bio2BEL, etc.) are used to enrich along the sad 
nodes to determine if they have already been curated. Those that are found in other sources are marked as 
happy.

4. Gather statements from INDRA
-------------------------------
First, the list of nodes can be sent directly to INDRA to find statements containing them. Before giving
 to a manual curator, several steps are taken:

1. Filter statements containing chemicals (this will be done in a later round of curation)
2. Calculate confidences on statements
3. Choose one evidence for each statement to present to the curator
4. Query INDRA for all citations of statements presented to the curator, and find other statements from 
those citations
5. Sort by citation, then evidence.

5. Curation
-----------
Besides the provendance, evidence string, and BEL statement, there are 4 columns to fill during curation:

1. Checked
2. Correct
3. Changed
4. Annotations

After checking the statement, an "x" should be placed in the "Checked" column. If the statement was correct, 
an "x" should be placed in the "Correct" column. Otherwise, the statement should be fixed (assignment of 
entity types, relation, etc.) and an "x" should be placed in the "Changed" column. If the statement is total 
nonsense, then no checks should be placed in either the "Correct" or "Changed" columns.

If there are other BEL that can be extracted, make a new line with all of the same provenance information 
(uuid, reference, evidence, etc.) and just place an "x" in the "Changed" column.

If there are any annotations (cell type, species, cell line, tissue, experimental context, etc.) that are 
obvious from the evidence, then they can be denoted in this column as BEL ``SET ANNOTATION ...`` statements.

6. Re-curation
--------------
The curation spreadsheets can be readily serialized to BEL, and the recuration 
procedure can be followed by an independent curator. For high-importance 
statements, the curation procedure can be done by two independent curators, 
recuration can be done by two independent curators, and finally a meeting to 
decide on inter-annotator agreement can be held.

The full re-curation guidelines can be found at: https://gitlab.scai.fraunhofer.de/charles.hoyt/curation-guidelines/blob/master/Recuration.rst

7. Assignment of NeuroMMSig Subgraphs
-------------------------------------
First, a simple rule set can be used to assign edges to a subgraph.

Full Confidence Rules
~~~~~~~~~~~~~~~~~~~~~
1. If both the subject and object already appear in the subgraph
2. If only one of the subject and object appears in the subgraph, and the other is a non-molecular 
   actor (chemical, biological processes, pathology)
