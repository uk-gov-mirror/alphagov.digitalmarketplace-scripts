from pathlib import Path
from unittest import mock

from dmscripts.email_engine.cli import argument_parser_factory


class TestArgumentParser:
    def test_dry_run(self):
        argument_parser = argument_parser_factory()
        assert argument_parser.parse_args([]).dry_run is False
        assert argument_parser.parse_args(["--dry-run"]).dry_run is True
        assert argument_parser.parse_args(["-n"]).dry_run is True

    def test_notify_api_key_from_envvar(self):
        with mock.patch.dict("os.environ", {"DM_NOTIFY_API_KEY": "test-api-key"}):
            args = argument_parser_factory().parse_args([])

        assert args.notify_api_key == "test-api-key"

    def test_notify_api_key_from_envvar_and_argv(self):
        with mock.patch.dict("os.environ", {"DM_NOTIFY_API_KEY": "old-api-key"}):
            args = argument_parser_factory().parse_args(
                ["--notify-api-key=new-api-key"]
            )

        assert args.notify_api_key == "new-api-key"

    def test_notify_api_key_is_none_if_not_set_by_environment_or_cli(self):
        with mock.patch.dict("os.environ", clear=True):
            args = argument_parser_factory().parse_args([])

        assert args.notify_api_key is None

    def test_reference_default_is_sys_argv_0(self):
        with mock.patch("sys.argv", ["foobar"]):
            args = argument_parser_factory().parse_args([])

        assert args.reference == "foobar"

    def test_reference_default_removes_suffix_dot_py(self):
        with mock.patch("sys.argv", ["foobar.py"]):
            args = argument_parser_factory().parse_args([])

        assert args.reference == "foobar"

    def test_reference_default_overridable_by_factory_arg(self):
        with mock.patch("sys.argv", ["foo"]):
            args = argument_parser_factory(reference="bar").parse_args([])

        assert args.reference == "bar"

    def test_reference_cli_argument_overrides_factory_arg(self):
        with mock.patch("sys.argv", ["foo"]):
            args = argument_parser_factory(reference="bar").parse_args(
                ["--reference=baz"]
            )

        assert args.reference == "baz"

    def test_default_logfile_path_is_derived_from_reference(self):
        with mock.patch("sys.argv", ["foo"]):
            args = argument_parser_factory().parse_args([])

        assert args.logfile == Path("/tmp/foo.log")

        with mock.patch("sys.argv", ["foo"]):
            args = argument_parser_factory(reference="bar").parse_args([])

        assert args.logfile == Path("/tmp/bar.log")
