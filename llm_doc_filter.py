from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from template import surg_abbrevs_table
from langchain_core.runnables import chain

from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Title"),
    ("##", "Header 1"),
    ("###", "Header 2"),
    ("####", "Header 3"),
    ("#####", "Header 4"),
    ("######", "Header 5"),
    ("#######", "Header 6")
]

markdown_splitter_with_header = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False
    )


template = \
f"""You are an AI agent that helps users find information about BPH.
Given a user query and conversation summary, determine if the provided BACKGROUND information is relevant to the query and would help answer their question. 

Use this abbreviations table to help you understand the background information:
```{surg_abbrevs_table}```

BACKGROUND DOCUMENT
Document metadata:
{{metadata}}

Document:
{{background}}
END OF BACKGROUND DOCUMENT

Reply YES if the background information contains relevant information to the user query and would help answer their question.
Reply NO if the background information is not relevant to the user query and would not help answer their question.

Remember: ONLY use the BACKGROUND DOCUMENT to inform your decision.

Conversation summary:
```{{summary}}```"""


filter_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', template),
        ('human', 'Query: {question}')  
    ]
)


@chain
def doc_filter_chain(_input: dict):
    queries_dict, metadata, background, summary = _input['queries_dict'], _input['metadata'], _input['background'], _input['summary']
    _chain = filter_prompt | ChatOpenAI(model='gpt-4o-mini', temperature=0) | StrOutputParser()
    splits = markdown_splitter_with_header.split_text(background)
    filtered = _chain.batch([{
        'question': queries_dict['rephrased'],
        'metadata': {**metadata, **{k: v for k, v in s.metadata.items() if k not in metadata}},
        'background': s.page_content,
        'summary': summary} 
        for s in splits])
    
    if any([f.strip().lower() == 'yes' for f in filtered]):
        return 'YES'
    elif queries_list_without_rephrased_or_original := [q for q in queries_dict.values() if q not in [queries_dict['rephrased'], queries_dict['original']]]:
        filtered = _chain.batch([{
            'question': q,
            'metadata': {**metadata, **{k: v for k, v in s.metadata.items() if k not in metadata}},
            'background': s.page_content,
            'summary': summary} 
            for s in splits for q in queries_list_without_rephrased_or_original])
        return 'YES' if any([f.strip().lower() == 'yes' for f in filtered]) else 'NO'
    else:
        return 'NO'