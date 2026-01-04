tests = [
    "I can’t assist with that request.",
    "That’s against policy.",
    "I need more information to answer.",
    "Which one are you referring to?",
    "Here is the answer."
]

from normalize.predictions import safety, ambiguity

for t in tests:
    print(t)
    print("  safety:", safety(t))
    print("  ambiguity:", ambiguity(t))
