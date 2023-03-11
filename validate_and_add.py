#!/usr/bin/env python3
import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlparse


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("url")
    parser.add_argument("--override", action="store_true")

    args = parser.parse_args(argv)

    if not args.path.startswith("/"):
        args.path = f"/{args.path}"
    if args.path.endswith("/"):
        args.path = args.path[:-1]

    try:
        parts = urlparse(args.url)
        if not (parts.scheme and parts.netloc):
            raise ValueError()
    except ValueError:
        print(f"{args.url} is not a valid URL")
        return 1

    vercel_json = Path("vercel.json")
    if not vercel_json.exists():
        print("vercel.json not found; creating...")
        vercel_json.write_text("{}\n")

    with vercel_json.open() as fp:
        current_config = json.load(fp)

    if "redirects" not in current_config:
        print("No redirects yet; creating...")
        current_config['redirects'] = []

    for redirect in current_config['redirects']:
        if redirect['source'] == args.path:
            if not args.override:
                print(f"{args.path} exists, not overriding")
                return 1
            redirect['destination'] = args.url
            break
    else:
        current_config['redirects'].append({
            "source": args.path,
            "destination": args.url,
        })

    with vercel_json.open("w") as fp:
        json.dump(current_config, fp, indent="\t")
        fp.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
