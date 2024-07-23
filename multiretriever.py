from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import chain
import json
from langchain.load import dumps, loads
from template import meds_abbrevs_table, surg_abbrevs_table, other_abbrevs_table

template = f"""ABBREVIATIONS
{meds_abbrevs_table}

{surg_abbrevs_table}

{other_abbrevs_table}
END OF ABBREVIATIONS

You are part of an AI team that helps users find information about BPH.
Given a user query, decide if it needs to be broken down into subquestions, in order to maximize retrieval in a vector search.

Rules:
- Only create subquestions if the query asks about different diagnostic tests, medical treatments, or surgical treatments for BPH.
- If you determine subquestions are needed, create short and succinct subquestions, each focusing on just a single treatment from the original question.
- For treatments with multiple names/abbreviations/examples/equivalents/brand Names, include all known names/abbreviations in the subquestions.
- Do not repeat any questions.
- You may generate as many as necessary, depending on how many subquestions you think are needed to cover the full scope of the original question.
- Finally, provide a single, rephrased version of the original question that encompasses all the subquestions.

Remember: If you determine that the original question does not need to be broken down, return just the single rephrased version of the original question.

For all subquestions, including the rephrased question: don't forget to include all known names/abbreviations for each treatment in the subquestions.

Return just a JSON object in exactly this template; each subquestion should only cover a single treatment, and the rephrased question should encompass all treatments in the original question: 

```json
{{
    "q1": ...,
    "q2": ...,
    ...,
    "qn": ...,
    "rephrased": ...
}}
```"""


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=template),
        ('human', 'Query: {question}')
    ]
)

@chain
def generate_queries(question: str):
    generate = prompt | ChatOpenAI(model='gpt-4o', temperature=0) | StrOutputParser()
    qs = generate.invoke(question)
    qs = json.loads(qs.strip('```json\n').strip('```'))
    qs['original'] = question
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
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    
    # Initialize a dictionary to hold fused scores for each unique document
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
    return [d for d,s in reranked_results]