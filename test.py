from dotenv import load_dotenv
import pytest

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Run pytest with verbosity and specify the tests directory
    exit_code = pytest.main(["-v", "tests"])
    exit(exit_code)
