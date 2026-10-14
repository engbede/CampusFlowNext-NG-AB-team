# CampusFlow AI Learning Log

## Engineer B: Search, Reports, and CLI

### Learning Cycle 1: CLI Test Debugging

**Problem:** A CLI test failed because it expected the
created ticket's title to appear in the captured output.

**Prompt used:**

"please make the changes and give me the full correct code in tests/test_cli.py"

**AI guidance:** Review the test's assertions and ensure
that the expected behaviour matches the actual CLI output
and stored ticket data.

**Independent verification:**
- Corrected `tests/test_cli.py`.
- Ran `python3 -m py_compile tests/test_cli.py`.
- Ran `python3 -m unittest tests.test_cli -v`.
- Observed 16 passing CLI tests.

**Decision:** Modified the test instead of requiring the
CLI to print the title. The corrected test checks the success
message, ticket ID, priority, collection length, and stored
title. This verifies that the ticket was created correctly
without assuming that the CLI displays information it does
not currently display.

### Learning Cycle 2: Search and Reporting

**Problem:** Implement and test ticket search and reporting
features without replacing the existing application.

**Prompt used:**

[Replace this line with the exact prompt you used to request
the search and reporting implementation.]

**AI guidance:**

The implementation guidance separated search logic from
the command-line interface and reporting logic. Search
supports case-insensitive title matching and optional
category, status, and priority filters. The filters combine
using AND logic. Reporting calculates ticket totals,
distributions, unresolved and resolved counts, and the
resolution percentage.

**Independent verification:**
- Ran `python3 -m unittest discover -s tests -v`.
- Observed 91 passing tests and no failures.
- Added or updated tests for search, reporting, and CLI
  behaviour.
- The recorded test result confirms that the full suite
  passed at that point; additional assignment requirements
  still need to be checked separately.

**Decision:** Accepted the search and reporting approach
because it adds the requested features while retaining the
existing application structure. The implementation was
checked using automated tests rather than relying only on
the AI-generated code.

### Required Reflection

**One AI suggestion changed, improved, or rejected:**

The initial test expectation assumed that the created ticket's
title would appear in the captured CLI output. That assertion
was changed because the current CLI does not print the title
in its success message.

**Evidence supporting the decision:**

The revised test checks the creation success message, ticket
ID, priority, number of stored tickets, and the title saved
in the ticket collection. The CLI test suite passed all
16 tests after the correction.

**Independent experiment:**

**Independent experiment:**

I created two sample tickets: one in the Network category
and another in the Hardware category. Both ticket titles
contained the word "network".

I searched using the title query "network" and the category
filter "Network".

**Expected result:** Only T001 should be returned because
it matches both filters.

**Actual result:** [Record the output you observed.]

**Conclusion:** [State whether the actual result matched
the expected result.]

**What I learned:**

I learned that automated tests should verify the application's
actual requirements rather than assume how its output should
look. I also learned that search filters can be combined
using AND logic, so a ticket must satisfy every active filter
to appear in the results.

I learned that reporting functions should calculate their
results from the current ticket collection. Empty collections
need special handling so the resolution percentage does not
cause a division-by-zero error.

Finally, separating search, reporting, and CLI responsibilities
makes the code easier to test and maintain.

**What I would do differently:**

Next time, I would inspect the existing implementation and
tests before changing code. I would write down the expected
behaviour for each feature, add focused tests, implement one
feature at a time, and run the relevant tests after each
change. I would then run the complete test suite to check
for regressions.

I would also keep exact AI prompts and record my own
experiments as I work, rather than trying to reconstruct
them afterwards.