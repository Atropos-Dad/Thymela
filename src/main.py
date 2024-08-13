import asyncio
import sys
from tqdm import tqdm
import logging
from searching.setup_and_index import init_and_index


    

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



def main():
    # 
    asyncio.run(init_and_index(run_init_default=True))
  
if __name__ == "__main__":
    main()