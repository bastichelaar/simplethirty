import json
import sys

from simplethirty import utils
from simplethirty.api import request

##
# List resources
##
@utils.arg('type',
       default="app",
       choices=["app", "repository"],
       help="Type of the resources to list.")
def list(args):
    """List all resources of a type."""

    url = "%s/%s/" % (args.base_url, args.type)
    context = {"username": args.username, "password": args.password}

    try:
        response = request(
                url,
                method='GET',
                context=context)
    except:
        sys.stderr.write("Could not connect to the API...")
        sys.exit(2)

    if response.status_code in [200, 201, 204]:
        if response.content:
            response_dict = json.loads(response.content)
            for item in response_dict["items"]:
                sys.stdout.write(item['name'] + "\n")
    else:
        sys.stderr.write("Something went wrong...")
