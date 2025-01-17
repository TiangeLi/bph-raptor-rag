from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain, RunnableParallel
import json
from langchain.load import dumps, loads
from template import meds_abbrevs_table, surg_abbrevs_table, other_abbrevs_table
from constants import MULTIQUERYLLM, REPHRASINGLLM, REORGLLM


sys_template_root = f"ABBREVIATIONS\n\n{meds_abbrevs_table}\n\n{surg_abbrevs_table}\nEND OF ABBREVIATIONS"

sys_template_multi = f"""{sys_template_root}

Your task is to generate subquestions from the Query. 

Rules:
- One subquestion per ENTITY from the query
- Each entity should be referred to by all of its names and abbreviations, per the tables provided.

```json
{{{{
    "q1": ...,
    "q2": ...,
    ...,
    "qn": ...,
}}}}
```"""

sys_template_rephrase = f"""{sys_template_root}

You are part of an AI team that helps users find information about BPH.
Given a user query and conversation context, rephrase it to maximize retrieval in a vector search.

Rules:
- Rephrase the question to be as clear and concise as possible, while still covering the full scope of the original question.
- The rephrased question should be a single query that encompasses all the information/treatments in the original question.
- For treatments with multiple names/abbreviations/examples/equivalents/brand Names, include all known names/abbreviations in the subquestions.

Return only the rephrased query, without adding any additional extraneous information or commentary.

Remember to expand all abbreviations, then include all related terms using the provided tables."""


sys_template_reorg = f"""{sys_template_root}

Your task is to use the above tables to rephrase the query so that like items are grouped, and equivalent terms are combined."""


multi_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', sys_template_multi),
        ('ai', "{treatments}\n\nConversation Context:\n{summary}"),
        ('human', 'Query: {question}')
    ]
)
rephrase_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', sys_template_rephrase),
        ('ai', "{treatments}\n\nConversation Context:\n{summary}"),
        ('human', 'Query: {question}')
    ]
)

reorg_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', sys_template_reorg),
        ('human', '{question}')
    ]
)


def recs_string(tx_options: dict):
    def _flatten(_input: dict):
        return ', '.join([i for _, v in _input.items() if v for i in v])
    strings = []
    if tx_options.get('size'):
        strings.append(f'Based solely on the patient\'s prostate size, guidelines recommend {_flatten(tx_options["size"])}')
    if tx_options.get('q_s'):
        strings.append(f'Based solely on the patient\'s interest in preservation of sexual function (including erectile & ejaculatory function), guidelines recommend {_flatten(tx_options["q_s"])}')
    if tx_options.get('q_m'):
        strings.append(f'Based solely on the patient\'s medical complexity (i.e. unfit or cannot have anesthesia), guidelines recommend {_flatten(tx_options["q_m"])}')
    if tx_options.get('q_b'):
        strings.append(f'Based solely on the patient\'s risk for bleeding / hematuria (e.g. patients on anticoagulation or antiplatelet therapy), guidelines recommend {_flatten(tx_options["q_b"])}')
    return '\n\n'.join(strings)

def _rephrase_reorganize_chain(_input: dict):
    _rephrase_chain = rephrase_prompt | REPHRASINGLLM | StrOutputParser()  # gpt-4o
    _reorg_chain = reorg_prompt | REORGLLM | StrOutputParser()  # gpt-4o-mini
    _rephrased = _rephrase_chain.invoke(_input)
    _reorg = _reorg_chain.invoke({'question': _rephrased})
    return {'rephrased': _rephrased, 'reorganized': _reorg}
        
@chain
def generate_queries(_input: dict):
    q_raw, summary, _tx_options = _input['question'], _input['summary'], _input['tx_options']
    treatments = recs_string(_tx_options)

    _multi_chain = multi_prompt | MULTIQUERYLLM | StrOutputParser()  # gpt-4o

    _chain = RunnableParallel(__m=_multi_chain, __r=_rephrase_reorganize_chain)
    _qs = _chain.invoke({'question': q_raw, 'summary': summary, 'treatments': treatments})
    _qs_multi = json.loads(_qs['__m'].strip('```json\n').strip('```'))
    _qs_rephrase = _qs['__r']['rephrased']
    _qs_reorg = _qs['__r']['reorganized']

    qs = {**_qs_multi, 'rephrased': _qs_rephrase, 'reorganized': _qs_reorg, 'original': f"Query: {q_raw}\n\n{treatments}\n\n{summary}"}
    return qs


def get_unique_union(documents: list[list]):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]


def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}

    # Iterate through each list of ranked documents
    for docs in results:
        # Iterate through each document in the list, with its rank (position in the list)
        for rank, doc in enumerate(docs):
            # Convert the document to a string format to use as a key (assumes documents can be serialized to JSON)
            doc_str = dumps(doc)
            # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            # Retrieve the current score of the document, if any
            previous_score = fused_scores[doc_str]
            # Update the score of the document using the RRF formula: 1 / (rank + k)
            fused_scores[doc_str] += 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Return the reranked results as a list of tuples, each containing the document and its fused score
    return [d for d,_ in reranked_results]