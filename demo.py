import argparse
import json

from ali_sandbox.demo_scripts import build_initial_demo_code
from ali_sandbox.self_healing import run_self_healing_bridge


def main():
    parser = argparse.ArgumentParser(description="Run Gurveer's ALI sandbox bridge.")
    parser.add_argument(
        "--failure",
        default="bad_endpoint",
        choices=["bad_endpoint", "missing_auth", "wrong_field", "syntax_error", "timeout"],
    )
    parser.add_argument("--mode", default="safe_demo", choices=["safe_demo", "discord_live", "full_live"])
    parser.add_argument("--timeout", type=int, default=5)
    args = parser.parse_args()

    initial_code = build_initial_demo_code(args.failure, args.mode)
    result = run_self_healing_bridge(initial_code, mode=args.mode, timeout_seconds=args.timeout)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
