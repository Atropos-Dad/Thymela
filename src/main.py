import asyncio
import sys
import logging
from searching.setup_and_index import init_and_index
from webapp.app import create_app

fh = logging.FileHandler("debug.log", encoding="utf-8")
sh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
sh.setLevel(logging.INFO)

handlers = [sh,fh]
# if args.debug:
#     handlers.append(fh)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    # format="%(asctime)s [%(levelname)s] %(message)s",
    # format with filename and line number
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
    handlers=handlers,
)

async def main():
    await init_and_index(run_init_default=True)
    app = await create_app()
    return app

if __name__ == "__main__":
    app = asyncio.run(main())
    app.run(debug=True)