from arxml_codegen.cli import build_parser


def test_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.config.parts[-2:] == ("config", "project.yaml")
    assert args.dry_run is False
    assert args.create_template is None
