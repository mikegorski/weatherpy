import cyclopts

from .config import handle_config

app = cyclopts.App(help="Weather forecast in your command line.")


@app.default
def wthr():
    """Shows the latest weather forecast based on default settings from the
    configuration file (if no arguments are provided).
    Every setting can be optionally overridden using arguments provided to this command.
    """
    config = handle_config()
    # below code for testing purposes
    s = config.sections()[0]
    for n in config[s]:
        print(n, config[s][n])


@app.command
def latest():
    """Show weather forecast at location and in format based on your latest request."""
    ...


if __name__ == "__main__":
    app()
