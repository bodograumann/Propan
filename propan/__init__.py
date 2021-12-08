import argparse
import importlib
import sys

from loguru import logger
import uvloop

from propan.config.settings import init_settings
from propan.startproject import create


def run():
    global args
    parser = argparse.ArgumentParser(description='Simple start with async rabbitmq consumers!')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", type=str, help="Select entrypoint of your consumer", nargs='?')
    group.add_argument("-s", "--start", metavar="DIRNAME", type=str, help="Input project name to create", nargs='?')
    parser.add_argument("-W", "--workers", metavar="10", default=10, type=int,  help="Select number of workers")
    parser.add_argument("-C", "--config", metavar="CONFIG_FILE.yml", default="config.yml", type=str, help="Select conf file of your consumer")
    parser.add_argument('-R', '--reload', dest='reload', action='store_true')
    args = parser.parse_args()
    
    if (dirname := args.start):
        create(dirname)
    else:
        if args.reload:
            from propan.supervisors.watchgodreloader import WatchGodReload
            WatchGodReload(target=_run).run()
        else:
            _run()

def _run():
    uvloop.install()
    config = init_settings(args.config, **{
        "MAX_CONSUMERS": args.workers
    })
    sys.path.append(config.BASE_DIR)

    try:
        f, func = args.file.split(":", 2)
        mod = importlib.import_module(f)
        app = getattr(mod, func)
    except ValueError:
        logger.error('Please, input module like python_file:propan_app_name')
    else:
        app.run()