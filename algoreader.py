aua_surg_algo = """AUA Decision Tree for Surgical Management of LUTS

Small Prostate (<30cc): HoLEP, PVP, ThuLEP, TIPD, TUIP, TURP, TUVP
Average Prostate (30-80cc): RWT, HoLEP, PVP, PUL, ThuLEP, TIPD, TURP, TUVP, WVTT
Large Prostate (80-150cc) or Very Large Prostate (>150cc): Simple Prostatectomy (Open, Laparoscopic, Robotic), HoLEP, ThuLEP

Patients Concerned with Preservation of Erectile and Ejaculatory Function: PUL, WVTT

Medically Complicated Patients (Higher Risk of Bleeding, on Anticoagulation Drugs)
  - Recommended Surgical Options with Lower Need for Blood Transfusion: HoLEP, PVP, ThuLEP"""

cua_surg_algo = """CUA Decision Tree for Surgical Management of LUTS

Small Prostate (<30cc): TUIP, M/B-TURP, Urolift
Average Prostate (30-80cc): M/B-TURP, Greenlight PVP, AEEP, Urolift, Rezum, TUMT, Aquablation
Large Prostate (>80cc) or Very Large Prostate (>150cc): OSP, AEEP, Greenlight PVP, B-TURP, Aquablation

Medically complicated patients:
  - Not fit for or unable to undergo anesthesia: TUMT, Urolift, Rezum, iTIND
  - Unable to discontinue antiplatelet/anticoagulation medication: AEEP, Greenlight PVP"""

eau_surg_algo = """EAU Decision Tree for Surgical Management of LUTS

Small Prostate (<30cc): TUIP, TURP
Average Prostate (30-80cc): TURP, laser enucleation, bipolar enucleation, laser vaporisation, PU Lift / Urolift
Large Prostate (>80cc) or Very Large Prostate (>150cc): Open prostatectomy, HoLEP, bipolar enucleation, laser vaporisation, thulium enucleation, TURP

Medically complicated patients:
  - Not fit for or unable to undergo anesthesia: PU Lift / Urolift
  - Unable to discontinue antiplatelet/anticoagulation medication: laser vaporisation, laser enucleation

* Laser vaporisation includes GreenLight, thulium, and diode laser vaporisation.
* Laser enucleation includes holmium and thulium laser enucleation (HoLEP, ThuLEP)"""







algo_template = \
"""You're an AI assistant that helps users find information about BPH.
Given a user query, use the given decision tree algorithm to provide just a list of surgical options relevant to the user.

If the user query is not relevant or applicable to this decision tree, reply None
If the user query is relevant BPH management, especially if with respect to surgical therapies, prostate size, sexual function, medical complexity (including patients at risk of bleeding, taking anticoagulation, or who cannot have anesthetics), or other related topics, reply using the response template.

Template: treatment1, treatment2, treatment3, ...
Example: TURP, PVP, TUIP

Algorithm:
```{algo}```

Conversation summary:
{summary}"""


from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', algo_template),
        ('human', 'Query: {question}')
    ]
)
tx_algo_chain = prompt | ChatOpenAI(model='gpt-4o-mini', temperature=0) | StrOutputParser()