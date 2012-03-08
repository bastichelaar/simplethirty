import sys

from simplethirty import utils
from simplethirty.api import request

##
# Delete resources
##
@utils.arg('type',
        default=None,
        choices=["app", "repository"],
        help="Type of the resource to delete.")
@utils.arg('name',
        default=None,
        help="Name of the resource to delete.")
@utils.arg('--environment',
        default=None,
        metavar="environment",
        nargs="?",
        help="Work on a specific app environment. This option only \
applies for app resources."
            )
def delete(args):
    """Delete a resource."""
    if args.environment:
        url = "%s/%s/%s/environment/%s/" % (
                args.base_url,
                args.type,
                args.name,
                args.environment)
    else:
        url = "%s/%s/%s/" % (args.base_url, args.type, args.name)

    context = {"username": args.username, "password": args.password}
    try:
        response = request(
                url,
                method='DELETE',
                context=context)
    except:
        pass

    if response.status_code == 204:
        sys.stdout.write("%s %s deleted" % (
            args.type.capitalize(), args.name))
    elif response.status_code == 404:
        sys.stderr.write("%s %s not found" % (
            args.type.capitalize(), args.name))
    elif response.status_code < 500:
        sys.stderr.write("Something went wrong...")
