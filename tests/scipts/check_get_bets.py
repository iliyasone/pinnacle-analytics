import subprocess
import sys
import time

import requests

BASE_URL = "http://localhost:8000"
API_KEY = "test-key-only"


def run_cmd(cmd: list[str]):
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result.stdout


try:
    # add API key
    run_cmd(["uv", "run", "python", "manage_api_keys.py", "add", API_KEY])

    # give the server a moment if needed
    time.sleep(0.2)

    # call endpoint
    response = requests.post(
        f"{BASE_URL}/get_bets",
        headers={
            "accept": "application/json",
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        json={"days": 1},
        timeout=10,
    )

    print("Status code:", response.status_code)
    print("Response body:", response.text)

    response.raise_for_status()

finally:
    # always attempt cleanup
    run_cmd(["uv", "run", "python", "manage_api_keys.py", "delete", API_KEY])
