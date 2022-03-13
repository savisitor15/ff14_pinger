
import logging
import asyncio
import argparse
import ff14pinger

#Setup logging
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dcFilename", help="json file containing the names and ips of datacenters", default="server_list.json")
    args = parser.parse_args()
    app = ff14pinger.main
    asyncio.run(app(args.dcFilename))