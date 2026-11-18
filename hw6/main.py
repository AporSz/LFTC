import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    hw6_directory = Path(__file__).resolve().parent
    argument_parser = argparse.ArgumentParser(
        description="Build and run the IoT-Script parser using yacc and Flex."
    )
    argument_parser.add_argument(
        "--mode",
        choices=("pif", "source"),
        default="pif",
        help="read PIF.csv/ST.csv or tokenize source with Flex (default: pif)",
    )
    argument_parser.add_argument(
        "--pif",
        type=Path,
        default=hw6_directory / "PIF.csv",
        help="PIF CSV input (used in pif mode)",
    )
    argument_parser.add_argument(
        "--st",
        type=Path,
        default=hw6_directory / "ST.csv",
        help="symbol table CSV input (used in pif mode)",
    )
    argument_parser.add_argument(
        "--source",
        type=Path,
        default=hw6_directory / "sample_code.txt",
        help="source input (used in source mode)",
    )
    args = argument_parser.parse_args()

    tools = ("yacc", "flex", "gcc")
    missing_tools = [tool for tool in tools if shutil.which(tool) is None]
    if missing_tools:
        argument_parser.error(
            "required tool(s) not found: " + ", ".join(missing_tools)
        )

    with tempfile.TemporaryDirectory(prefix="hw6-yacc-") as build_directory:
        build_path = Path(build_directory)
        subprocess.run(
            [
                "yacc",
                "-d",
                "-o",
                str(build_path / "y.tab.c"),
                str(hw6_directory / "parser.y"),
            ],
            cwd=build_path,
            check=True,
        )
        subprocess.run(
            [
                "flex",
                "-o",
                str(build_path / "lex.yy.c"),
                str(hw6_directory / "lexer.l"),
            ],
            cwd=build_path,
            check=True,
        )
        executable = build_path / "hw6_parser"
        subprocess.run(
            [
                "gcc",
                "-o",
                str(executable),
                str(build_path / "y.tab.c"),
                str(build_path / "lex.yy.c"),
            ],
            cwd=build_path,
            check=True,
        )

        if args.mode == "pif":
            parser_command = [
                str(executable),
                "--pif",
                str(args.pif.resolve()),
                str(args.st.resolve()),
            ]
        else:
            parser_command = [
                str(executable),
                "--source",
                str(args.source.resolve()),
            ]

        return subprocess.run(parser_command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
