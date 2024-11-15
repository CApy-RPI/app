import unittest
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Discover all test cases in the 'tests' directory with pattern '*_test.py'
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="*_test.py")

    # Run tests with verbosity
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Exit with a non-zero code if tests fail (useful for CI/CD)
    if not result.wasSuccessful():
        exit(1)
