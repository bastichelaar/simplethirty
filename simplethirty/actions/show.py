import sys
import json

from simplethirty import utils
from simplethirty.api import request

##
# Show resources
##

@utils.arg('type',
        default=None,
        choices=["app", "repository"],
        help="Type of the resource to update.")
@utils.arg('name',
        default=None,
        help="Name of the resource to update.")
@utils.arg('--environment',
        default=None,
        help="The name of the default environment")
def show(args):
    """Show the details of a resource."""

    if args.environment:
        url = "%s/%s/%s/environment/%s/" % (
                args.base_url,
                args.type,
                args.name,
                args.environment)
    else:
        url = "%s/%s/%s/" % (
                args.base_url,
                args.type,
                args.name)

    context = {"username": args.username, "password": args.password}

    try:
        response = request(
                url,
                method='GET',
                context=context)
    except:
        pass

    if response.content:
        sys.stdout.write(json.dumps(json.loads(response.content), sort_keys=True, indent=4))
