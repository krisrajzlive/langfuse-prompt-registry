import argparse
import json
from pathlib import Path

from . import chains, registry
from .config import Settings


def main() -> None:
    p = argparse.ArgumentParser(prog="prompt-registry")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Verify credentials and connectivity")

    pub = sub.add_parser("publish", help="Publish a prompt definition as a new version")
    pub.add_argument("file", type=Path)

    pro = sub.add_parser("promote", help="Point a label at a version (also used for rollback)")
    pro.add_argument("name")
    pro.add_argument("version", type=int)
    pro.add_argument("label")

    run = sub.add_parser("run", help="Render a managed prompt and invoke it on Bedrock")
    run.add_argument("name")
    run.add_argument("--label", default="production")
    run.add_argument("--version", type=int)
    run.add_argument("--vars", required=True, help="JSON object of prompt variables")

    args = p.parse_args()
    settings = Settings.from_env()
    client = registry.get_client(settings)

    if args.cmd == "check":
        print("auth ok" if client.auth_check() else "auth failed")
    elif args.cmd == "publish":
        prompt = registry.publish(client, registry.load_definition(args.file))
        print(f"published {prompt.name} v{prompt.version} labels={prompt.labels}")
    elif args.cmd == "promote":
        registry.promote(client, args.name, args.version, args.label)
        print(f"{args.name}: label '{args.label}' -> v{args.version}")
    elif args.cmd == "run":
        prompt = registry.fetch(client, args.name, label=args.label, version=args.version)
        print(f"[{prompt.name} v{prompt.version}]")
        print(chains.run(prompt, json.loads(args.vars), settings))
    client.flush()


if __name__ == "__main__":
    main()
