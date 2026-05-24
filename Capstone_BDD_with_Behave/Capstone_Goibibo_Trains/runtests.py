import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ALLURE_RESULTS = PROJECT_ROOT / "reports" / "allure-results"


def run_command(command):
    print(f"\nRunning: {' '.join(command)}\n")
    return subprocess.run(command, cwd=PROJECT_ROOT).returncode


def clean_allure_results():
    if ALLURE_RESULTS.exists():
        shutil.rmtree(ALLURE_RESULTS)
    ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
    print(f"Cleaned Allure results: {ALLURE_RESULTS}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Behave BDD tests and generate Allure results."
    )
    parser.add_argument(
        "--tags",
        help="Behave tag expression, for example: @class, @positive, @negative, @e2e",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete old reports/allure-results before running tests.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Open the Allure report after the test run.",
    )
    args = parser.parse_args()

    if not args.no_clean:
        clean_allure_results()

    behave_command = [
        sys.executable,
        "-m",
        "behave",
        "-f",
        "allure_behave.formatter:AllureFormatter",
        "-o",
        str(ALLURE_RESULTS),
    ]
    if args.tags:
        behave_command.extend(["--tags", args.tags])

    test_exit_code = run_command(behave_command)

    if args.serve:
        allure_exit_code = run_command(["allure", "serve", str(ALLURE_RESULTS)])
        return test_exit_code or allure_exit_code

    print("\nTo open the Allure report, run:")
    print("allure serve reports/allure-results")
    return test_exit_code


if __name__ == "__main__":
    raise SystemExit(main())