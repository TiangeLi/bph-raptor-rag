PSIZE_AND_TX = \
    {"Not Known": "all available treatment options",
    "Enlarged (<80mL)": "B-TURP, M-TURP, Rezum, UroLift, Aquablation, Enucleation, GreenLight Laser Vaporization",
    "Very enlarged (80-150mL)": "Aquablation, Enucleation, GreenLight Laser Vaporization, Open simple prostatectomy, Robotic prostate removal", 
    "Extremely enlarged (>150 mL)": "Enucleation, GreenLight Laser Vaporization, Open simple prostatectomy, Robotic prostate removal"}
PSIZE_CATEGORIES = [i for i in PSIZE_AND_TX]
PSIZE_STRING = f'[{", ".join(PSIZE_CATEGORIES)}]'
_PSIZE_BULLET_LIST = "\n".join(f"- {i}" for i in PSIZE_CATEGORIES[1:])
AI_GREETING_MSG = \
f"""Hello! Ask me anything about surgical options for managing BPH (Benign Prostatic Hyperplasia)!

To best assist you, it would be helpful to know the size of your prostate, if you have been informed by your healthcare provider:
{_PSIZE_BULLET_LIST}

It's okay if you're not sure! I can provide an overview of all available surgical treatments or any specific questions about treatments."""


memory_template = \
"""I am a helpful agent. This is my personal memory of the conversation so far:

{summary}"""

summary_template = \
"""Analyze our conversation so far. Extract the following pertinent information and update your previous memory summary.
Return a JSON object. Be inclusive but concise.

"Prostate Size": "as provided by the user, if any; if not known, then say not known", 
"User Information": "ther important information, such as user's name, age, health status, medications, or other pertinent information",
"Last topics discussed": "which surgical treatments for BPH have been discussed with the user and in what context?\""""

template = \
"""BACKGROUND:
Surgical Treatment Options for BPH:
{context}
END OF BACKGROUND

INSTRUCTIONS:
Your MAIN GOAL is to have a normal conversation with the user.
Answer the USER's query. Focus on BPH Surgical Treatment only. Refuse politely but firmly to discuss any other topic.
Answer questions using ONLY the supplied information.
NEVER give an opinion. Instead, provide relevant information to help the User make their own decisions.

Focus your discussion on the treatments the User asks about.
If the user doesn't have questions about specific treatments, you can choose to discuss the relevant treatments for their prostate size:
"Not Known": "all available treatment options",
"Enlarged (<80mL)": "B-TURP, M-TURP, Rezum, UroLift, Aquablation, Enucleation, GreenLight Laser Vaporization",
"Very enlarged (80-150mL)": "Aquablation, Enucleation, GreenLight Laser Vaporization, Open simple prostatectomy, Robotic prostate removal", 
"Extremely enlarged (>150 mL)": "Enucleation, GreenLight Laser Vaporization, Open simple prostatectomy, Robotic prostate removal"

Use MARKDOWN TABLES or NESTED LISTS when discussing multiple treatments. 

*Do not overload the user with too much information all at once!
END OF INSTRUCTIONS

REMEMBER BACKGROUND INFORMATION AND INSTRUCTIONS
Your main goal is to have a normal conversation with the user.
Respond in layman language. Don't make reference to prostate size categories in your response.
Remember: answer using ONLY the BACKGROUND INFORMATION supplied in this prompt.

Do NOT make reference to the BACKGROUND INFORMATION in your answer."""

# ------------------------------------------------------------------- #

text="""Bipolar transurethral resection of the prostate (B-TURP)
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): NO
 - Extremely enlarged (>150 mL): NO 
How does it work: Bipolar TURP (B-TURP) is similar to M-TURP but uses a different type of controlled electrical current to remove prostate tissue. B-TURP is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications: This treatment can't be done on patients who have to stay on blood thinners.
Improvement to urinary symptoms: High
Improvement to quality of life: Significant
Risk of urinary retention after surgery: 4%
Average length of stay after surgery: 1 day
Average number of days a catheter is needed after surgery: 0.5 days
1 year retreatment rate due to prostate tissue regrowth: 9%
5 year retreatment rate due to prostate tissue regrowth: 15%
Urine leakage/incontinence after surgery: 1%
Problems with erections after surgery: 7%
Problems with ejaculation after surgery: 36%
Risk of blood transfusions after surgery: 2%
Risk of urinary tract infection/UTI after surgery: 4%
Cost: publicly funded

Monopolar transurethral resection of the prostate (M-TURP)
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): NO
 - Extremely enlarged (>150 mL): NO 
How does it work: M-TURP cuts prostate tissue with the help of a controlled electrical current. M-TURP is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications: This treatment can't be done on patients who have to stay on blood thinners.
Improvement to urinary symptoms: High
Improvement to quality of life: Significant
Risk of urinary retention after surgery: 4%
Average length of stay after surgery: 1 day
Average number of days a catheter is needed after surgery: 1 day
1 year retreatment rate due to prostate tissue regrowth: 9%
5 year retreatment rate due to prostate tissue regrowth: 15%
Urine leakage/incontinence after surgery: 2%
Problems with erections after surgery: 8%
Problems with ejaculation after surgery: 70%
Risk of blood transfusions after surgery: 4%
Risk of urinary tract infection/UTI after surgery: 4%
Cost: publicly funded

Rezum
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): NO
 - Extremely enlarged (>150 mL): NO 
How does it work: The Rezum treatment consists of injecting steam (water vapour) into the excess prostate tissue to kill the cells and shrink the enlarged prostate tissue. The treated tissue is then urinated or absorbed by the body over roughly 3 months, resulting in a smaller prostate. Rezum is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in the office setting in under 10 minutes using either: a local anesthetic (numbing gel inside the urethra and/or numbing the prostate using small injections of anesthesia around the prostate), or Light sedation (slightly asleep), or spinal anesthetic (frozen from the waist down), or a general anesthetic (asleep)
Contraindications:
Improvement to urinary symptoms: Medium
Improvement to quality of life: Medium
Risk of urinary retention after surgery: 4%
Average length of stay after surgery: none needed
Average number of days a catheter is needed after surgery: 3-7 days
1 year retreatment rate due to prostate tissue regrowth: 2%
5 year retreatment rate due to prostate tissue regrowth: 4%
Urine leakage/incontinence after surgery: none
Problems with erections after surgery: none
Problems with ejaculation after surgery: none
Risk of blood transfusions after surgery: none
Risk of urinary tract infection/UTI after surgery: 4%
Cost: \$5000-\$7000 / treatment

UroLift
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): NO
 - Extremely enlarged (>150 mL): NO 
How does it work: UroLift does not remove prostate tissue. Small implants are placed through the urethra and into the prostate where it is blocking urine flow. The sutures are permanent and work to pull apart the prostate tissue and open up the urethra. This technique is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in the office setting using either: spinal anesthetic (frozen from the waist down), or local anesthetic (numbing gel inside the urethra), conscious sedation (slightly asleep), or a general anesthetic (asleep).
Contraindications:
Improvement to urinary symptoms: Low
Improvement to quality of life: Medium
Risk of urinary retention after surgery: none
Average length of stay after surgery: none needed
Average number of days a catheter is needed after surgery: 1 day
1 year retreatment rate due to prostate tissue regrowth: 5%
5 year retreatment rate due to prostate tissue regrowth: 14%
Urine leakage/incontinence after surgery: 3%
Problems with erections after surgery: none
Problems with ejaculation after surgery: none
Risk of blood transfusions after surgery: none
Risk of urinary tract infection/UTI after surgery: none
Cost: \$8000-\$10000 / treatment

Aquablation
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): YES
 - Extremely enlarged (>150 mL): NO 
How does it work: Aquablation uses live imaging to view a patient's unique prostate anatomy. Then, a robotically controlled high-pressure water jet quickly removes the excess prostate tissue. Aquablation is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications:
Improvement to urinary symptoms: Medium
Improvement to quality of life: Significant
Risk of urinary retention after surgery: 9%
Average length of stay after surgery: 1 day
Average number of days a catheter is needed after surgery: 1 day
1 year retreatment rate due to prostate tissue regrowth: 3%
5 year retreatment rate due to prostate tissue regrowth: 7%
Urine leakage/incontinence after surgery: 2%
Problems with erections after surgery: none
Problems with ejaculation after surgery: 7%
Risk of blood transfusions after surgery: 4%
Risk of urinary tract infection/UTI after surgery: 9%
Cost: publicly funded

Enucleation
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): YES
 - Extremely enlarged (>150 mL): YES 
How does it work: Enucleation means removing tissue without cutting into it. This technique involves the complete removal of the excess prostate tissue from its outer shell, called the capsule. The excess prostate tissue is detached using a laser, pushed in the bladder and is later removed. This treatment is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications:
Improvement to urinary symptoms: High
Improvement to quality of life: Significant
Risk of urinary retention after surgery: none
Average length of stay after surgery: 1 day
Average number of days a catheter is needed after surgery: 1 day
1 year retreatment rate due to prostate tissue regrowth: none
5 year retreatment rate due to prostate tissue regrowth: none
Urine leakage/incontinence after surgery: 6%
Problems with erections after surgery: none
Problems with ejaculation after surgery: 74%
Risk of blood transfusions after surgery: none
Risk of urinary tract infection/UTI after surgery: 5%
Cost: publicly funded

GreenLight Laser Vaporization
Optimal prostate size: 
 - Enlarged (<80mL): YES
 - Very enlarged (80-150mL): YES
 - Extremely enlarged (>150 mL): YES 
How does it work: Vaporization means heating a liquid or solid substance so that it can turn into a gas. GreenLight laser energy is aimed onto the enlarged prostate tissue, which is then heated until it gets turned into gas and is removed. This treatment is done with a thin tube-like camera through the urethra and there is no need to make any cuts on the skin.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications:
Notes: can be done on patients who take blood thinners, without having to stop/hold those medications
Improvement to urinary symptoms: Medium
Improvement to quality of life: Significant
Risk of urinary retention after surgery: 4%
Average length of stay after surgery: 0.5-1 days
Average number of days a catheter is needed after surgery: 1 day
1 year retreatment rate due to prostate tissue regrowth: 12%
5 year retreatment rate due to prostate tissue regrowth: 1%
Urine leakage/incontinence after surgery: 3%
Problems with erections after surgery: none
Problems with ejaculation after surgery: 66%
Risk of blood transfusions after surgery: none
Risk of urinary tract infection/UTI after surgery: 18%
Cost: publicly funded

Open prostate removal (simple prostatectomy)
Optimal prostate size: 
 - Enlarged (<80mL): NO
 - Very enlarged (80-150mL): YES
 - Extremely enlarged (>150 mL): YES 
How does it work: An open prostate removal requires making a cut on the skin right below the belly button to be able to remove the enlarged tissue of the prostate.
Anesthesia: Performed in an operating room using either: a general anesthetic (asleep), or a spinal anesthetic (frozen from the waist down).
Contraindications:
Improvement to urinary symptoms: Medium
Improvement to quality of life: Medium
Risk of urinary retention after surgery: 5%
Average length of stay after surgery: 3 days
Average number of days a catheter is needed after surgery: 3-7 days
1 year retreatment rate due to prostate tissue regrowth: none
5 year retreatment rate due to prostate tissue regrowth: 5%
Urine leakage/incontinence after surgery: 3%
Problems with erections after surgery: 8%
Problems with ejaculation after surgery: 80%
Risk of blood transfusions after surgery: 9%
Risk of urinary tract infection/UTI after surgery: 13%
Cost: publicly funded

Robotic prostate removal
Optimal prostate size: 
 - Enlarged (<80mL): NO
 - Very enlarged (80-150mL): YES
 - Extremely enlarged (>150 mL): YES 
How does it work:  Robotic prostate removal is similar to an open prostate removal. However, instead of one large cut on the skin, many keyhole incisions and 1 larger cut are made.
Anesthesia: Performed in an operating room using a general anesthetic (asleep).	
Contraindications:
Improvement to urinary symptoms: Medium
Improvement to quality of life: Medium
Risk of urinary retention after surgery: 6%
Average length of stay after surgery: 1-2 days
Average number of days a catheter is needed after surgery: 7 days
1 year retreatment rate due to prostate tissue regrowth: none
5 year retreatment rate due to prostate tissue regrowth: 5%
Urine leakage/incontinence after surgery: 2%
Problems with erections after surgery: none
Problems with ejaculation after surgery: 80%
Risk of blood transfusions after surgery: 11%
Risk of urinary tract infection/UTI after surgery: 11%
Cost: publicly funded"""