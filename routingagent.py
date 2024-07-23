from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from template import meds_abbrevs_table, surg_abbrevs_table, other_abbrevs_table

router_template = \
f"""ABBREVIATIONS
{meds_abbrevs_table}

{surg_abbrevs_table}

{other_abbrevs_table}
END OF ABBREVIATIONS

You're an AI assistant that helps users find information about BPH
Available to you is a set of documents that contain information about BPH, including topics on evaluation, diagnosis, testing, medical therapies, surgical therapies, specific circumstances such as hematuria, medical complexity (including patients at risk of bleeding, taking anticoagulation, or who cannot have anesthetics), and more.
Given the user query, reply either YES or NO.

NO: if the user query is general/unrelated to BPH and does not require information from a BPH knowledge base
YES: if the user query is or could be about BPH and requires information from the knowledge base.

Conversation summary:
```{{summary}}```"""


router_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', router_template),
        ('human', 'Query: {question}')
    ]

)
router_chain = router_prompt | ChatOpenAI(model='gpt-4o-mini', temperature=0) | StrOutputParser()