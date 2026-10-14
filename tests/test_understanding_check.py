import unittest

from campusflow.understanding_check import QUESTIONS, score_answers


class TestScoreAnswers(unittest.TestCase):
    def test_all_correct_answers(self):
        answers = {
            index: question["answer"]
            for index, question in enumerate(QUESTIONS)
        }

        self.assertEqual(score_answers(answers), 6)

    def test_all_wrong_answers(self):
        answers = {
            index: (
                "A" if question["answer"] != "A" else "B"
            )
            for index, question in enumerate(QUESTIONS)
        }

        self.assertEqual(score_answers(answers), 0)

    def test_partial_score(self):
        answers = {
            0: QUESTIONS[0]["answer"],
            1: QUESTIONS[1]["answer"],
            2: "D",
        }

        self.assertEqual(score_answers(answers), 2)

    def test_lowercase_answers_are_accepted(self):
        answers = {
            index: question["answer"].lower()
            for index, question in enumerate(QUESTIONS)
        }

        self.assertEqual(score_answers(answers), 6)

    def test_missing_answers_are_not_correct(self):
        self.assertEqual(score_answers({}), 0)


if __name__ == "__main__":
    unittest.main()