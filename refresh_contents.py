#!/usr/bin/env python3
import json
import subprocess
import sys
import traceback
from argparse import ArgumentParser
from multiprocessing import Pool
from subprocess import Popen, PIPE, DEVNULL
from pathlib import Path

#import ipfshttpclient

parser = ArgumentParser(
    description=f"keep live"
)
subparsers = parser.add_subparsers(help="Command")
parser.set_defaults(command=lambda _: parser.print_help())

cmd_test_gateway = subparsers.add_parser(
    "keep_alive",
    description="downloading folder through a gateway as tar archive",
    epilog="keep_alive"
)
cmd_test_gateway.add_argument(
    "cid", help="cid of folder")


def download_with_curl(gateway,hash):

    # or api way
    url = f"https://{gateway}/api/v0/get?arg={hash}&archive=true"
    print('api ' + url)

    Path(f"./test/{gateway}").mkdir(parents=True, exist_ok=True)

    with open(f"./test/{gateway}/{hash}.log", "wb") as f:
        p = Popen(["curl", '-f', '-X','POST', url] , stdout=DEVNULL, stderr=f)
        p.wait() # wait for process to finish; this also sets the returncode variable inside 'res'
        #print(p.returncode)
        if p.returncode != 0:
            #print('chafa')
            raise Exception(f"{url} download failed, exit code {p.returncode}")
        else:
            print(f'finished downloading through {url}')

# def get_length(filename):
#     result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
#                              "format=duration", "-of",
#                              "default=noprint_wrappers=1:nokey=1", filename],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT)
#     return float(result.stdout)

def list_directory(gateway,cid):
    url = f"https://{gateway}/api/v0/ls?arg={cid}"
    p = Popen(["curl", '-s', '-f', '-X', 'POST', url], stdout=subprocess.PIPE, stderr=sys.stderr)
    result = p.communicate()[0] # wait for process to finish; this also sets the returncode variable inside 'res'
    # print(p.returncode)
    if p.returncode != 0:
        # print('chafa')
        raise Exception(f"{url} download failed, exit code {p.returncode}")
    else:
        return result.decode("utf-8")


def run_test_gateway(args):
    """
    test downloading through gateways
    """
    if __name__ == '__main__':
        gateways = [
            'ipfs.io', # the default one I use first, it uses 0.8.0
            'dweb.link',
            'jacl.tech', # pinning also works :)
        ]


        with Pool(10) as p:
            for gateway in gateways:
                resp = list_directory(gateway,args.cid)
                result = json.loads(resp)
                links = result["Objects"][0]["Links"]
                filtered_results = [link['Hash'] for link in links if link['Type'] == 2]

                arr = [(gateway, result,) for result in filtered_results]
                r = p.starmap_async(download_with_curl, arr )
                try:
                    r.get()
                except:
                    traceback.print_exc()





cmd_test_gateway.set_defaults(command=run_test_gateway)

# Finally, use the new parser
all_args = parser.parse_args()
# Invoke whichever command is appropriate for the arguments
all_args.command(all_args)
