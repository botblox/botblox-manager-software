"""Root commands for botblox manager."""

from .cli import cli


def main() -> None:
    """Execute on package entry point."""
    cli()


if __name__ == '__main__':
    main()
