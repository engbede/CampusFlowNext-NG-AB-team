QUESTIONS = [
    {
        "question": "What should happen if an unassigned open ticket is moved to in_progress?",
        "options": {
            "A": "The status should change",
            "B": "The operation should be rejected and the ticket should remain open",
            "C": "The ticket should be deleted",
            "D": "The ticket should be resolved",
        },
        "answer": "B",
        "explanation": (
            "A ticket must be assigned before it can move to in_progress. "
            "Rejecting the operation preserves the ticket's valid state."
        ),
    },
    {
        "question": "What should the resolution percentage be when there are no tickets?",
        "options": {
            "A": "100%",
            "B": "50%",
            "C": "An error",
            "D": "0%",
        },
        "answer": "D",
        "explanation": (
            "An empty collection has no resolved tickets. The report should "
            "return 0% and avoid division by zero."
        ),
    },
    {
        "question": "How should title, category, and status search filters combine?",
        "options": {
            "A": "Using AND, so every active filter must match",
            "B": "Using OR, so any filter can match",
            "C": "Only the title filter should be used",
            "D": "The filters should be ignored",
        },
        "answer": "A",
        "explanation": (
            "AND filtering returns tickets that satisfy every active search "
            "condition."
        ),
    },
    {
        "question": "Can a resolved ticket receive a note without being reopened?",
        "options": {
            "A": "Yes, always",
            "B": "Only if the author is an administrator",
            "C": "No, it must first be reopened",
            "D": "Only if its priority is high",
        },
        "answer": "C",
        "explanation": (
            "The requirements permit notes on open and in_progress tickets. "
            "A resolved ticket must be reopened before it can receive a note."
        ),
    },
    {
        "question": "What should happen when a JSON file contains duplicate ticket IDs?",
        "options": {
            "A": "Keep both tickets",
            "B": "Reject the data and preserve the existing in-memory collection",
            "C": "Delete all tickets from memory",
            "D": "Automatically change one ID",
        },
        "answer": "B",
        "explanation": (
            "Ticket IDs must be unique. Invalid stored data should be rejected "
            "without silently replacing valid in-memory data."
        ),
    },
    {
        "question": "A pull request changes validation but adds no negative tests. What should a reviewer do?",
        "options": {
            "A": "Approve immediately",
            "B": "Ignore the missing tests",
            "C": "Reject the entire project permanently",
            "D": "Request focused tests for invalid inputs",
        },
        "answer": "D",
        "explanation": (
            "Validation changes should be tested with invalid inputs as well "
            "as valid ones, so the reviewer should request focused negative tests."
        ),
    },
]


def score_answers(answers):
    """Return the number of correct answers."""
    score = 0

    for index, question in enumerate(QUESTIONS):
        if answers.get(index, "").strip().upper() == question["answer"]:
            score += 1

    return score


def run_understanding_check():
    """Ask the questions, calculate a score, and collect explanations."""
    answers = {}

    print("\n=== CampusFlow Engineering Understanding Check ===")
    print("Choose A, B, C, or D for each question.\n")

    for index, question in enumerate(QUESTIONS):
        print(f"Question {index + 1}: {question['question']}")

        for option, text in question["options"].items():
            print(f"  {option}. {text}")

        while True:
            answer = input("Your answer: ").strip().upper()

            if answer in question["options"]:
                answers[index] = answer
                break

            print("Invalid choice. Please enter A, B, C, or D.")

        print()

    score = score_answers(answers)
    print(f"Your score: {score}/{len(QUESTIONS)}")

    print("\n=== Answer Explanations ===")

    for index, question in enumerate(QUESTIONS):
        print(f"\nQuestion {index + 1}:")
        print(f"Correct answer: {question['answer']}")
        print(question["explanation"])

    print("\n=== Your Reflections ===")
    print("Please explain at least two answers in your own words.")

    for number in range(1, 3):
        while True:
            explanation = input(
                f"Your explanation for question {number}: "
            ).strip()

            if explanation:
                print(f"Recorded explanation: {explanation}")
                break

            print("Please enter an explanation before continuing.")

    return score