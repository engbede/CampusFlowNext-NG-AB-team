# CampusFlow Baseline Check

## Purpose

Record the application's behaviour and automated test results
before the CampusFlow Next enhancements.

## Environment

- Language: Python
- Interface: Command-line application
- Test framework: unittest
- Storage: JSON

## Baseline Automated Tests

Command:

`python3 -m unittest discover -s tests -v`

Recorded baseline result:

- Tests run: 78
- Passed: 78
- Failed: 0
- Overall result: OK

These results describe the original baseline, not the latest
version of the application.

## Manual Checks

The original document did not contain completed observations
for these checks. They must not be treated as verified results.

### Check 1: Open Work Queue

- Action: Open the work queue.
- Expected behaviour: Display open tickets in priority order.
- Actual result: Not recorded in the original baseline.
- Verification: Requires manual testing.

### Check 2: Reports

- Action: Open the ticket report.
- Expected behaviour: Display ticket totals and distributions.
- Actual result: Not recorded in the original baseline.
- Verification: Requires manual testing.

### Check 3: Exit

- Action: Select the exit menu option.
- Expected behaviour: The application exits cleanly.
- Actual result: Not recorded in the original baseline.
- Verification: Requires manual testing.

## Audit Observations

The following areas were identified for implementation or
verification during CampusFlow Next development:

- Search by title and combined filters.
- Category counts and resolution percentage in reports.
- Structured ticket follow-up notes.
- Engineering Understanding Check.
- JSON validation and ticket lifecycle safety.

## Conclusion

The original automated test suite passed all 78 tests.
The manual observations were not fully recorded in the
original document.

CampusFlow Next enhancements and regression tests are
documented separately.