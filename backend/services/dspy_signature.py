import os

import dotenv
import dspy

dotenv.load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY environment variable is required. "
        "Please set it in your .env file or environment variables."
    )

model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

lm = dspy.LM(
        model=model,
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
    )
dspy.configure(lm=lm)

io_sig = {
    "history": (dspy.History, dspy.InputField()),
    "candidate_answer": (str, dspy.InputField()),

    "question": (str, dspy.OutputField(desc="The interview question to ask the candidate. Could be a standalone question or a follow-up question.")),
    "is_followup": (bool, dspy.OutputField(desc="Whether this question is a follow-up to the previous answer")),
}
