# ==========================================
# ZERO-SHOT PROMPT
# ==========================================

def zero_shot_prompt(
    question,
    context
):

    return f"""
You are a helpful document question-answering assistant.

Answer the question using ONLY the provided document
context.

Document Context:
{context}

Question:
{question}

Instructions:
- Give a clear and concise answer.
- Do not use information outside the context.
- Do not invent facts.
- If the answer is not available in the context,
  say: "The answer is not available in the provided documents."

Answer:
"""


# ==========================================
# FEW-SHOT PROMPT
# ==========================================

def few_shot_prompt(
    question,
    context
):

    return f"""
You are a document question-answering assistant.

Answer questions using ONLY the provided document context.

Here are examples of the expected answer style:

Example 1:
Question: What is a variable?
Answer:
A variable is a name used to store a value.

Example 2:
Question: What is a function?
Answer:
A function is a reusable block of code that performs
a specific task.

Example 3:
Question: What is Python?
Answer:
Python is a high-level programming language.

Now use the same style to answer the user's question.

Document Context:
{context}

Question:
{question}

Rules:
- Use only the document context.
- Do not invent information.
- Keep the answer simple and accurate.
- If the answer is not available, say so.

Answer:
"""


# ==========================================
# ROLE-BASED PROMPT
# ==========================================

def role_based_prompt(
    question,
    context
):

    return f"""
You are an expert Technical Document Analyst
helping a student understand technical documents.

Your task is to answer the user's question using
ONLY the supplied document context.

Document Context:
{context}

User Question:
{question}

Follow these rules:

1. Act as a clear and patient technical teacher.
2. Use only information from the context.
3. Do not invent facts.
4. Explain difficult concepts in simple language.
5. Stay directly relevant to the question.
6. If the answer is not present in the context,
   say:
   "The answer is not available in the provided documents."

Technical Document Analyst Answer:
"""


# ==========================================
# GET SELECTED PROMPT
# ==========================================

def get_prompt(
    technique,
    question,
    context
):

    if technique == "zero-shot":

        return zero_shot_prompt(
            question,
            context
        )

    elif technique == "few-shot":

        return few_shot_prompt(
            question,
            context
        )

    elif technique == "role-based":

        return role_based_prompt(
            question,
            context
        )

    return zero_shot_prompt(
        question,
        context
    )