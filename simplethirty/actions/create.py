import sys
import json

from simplethirty import utils
from simplethirty.api import request

##
# Create resources
##
@utils.arg('type',
        default=None,
        choices=["app", "repository"],
        help="Type of the resource to create.")
@utils.arg('name',
        default=None,
        help="Name of the resource to create.")
@utils.arg('location',
        default=None,
        help="URL of the repository.")
@utils.arg('--flavor',
        default=None,
        help="The flavor of the app.")
@utils.arg('--environment',
        default="production",
        help="The name of the default environment")
@utils.arg('--root',
        default=".",
        help='the root directory of the application')
@utils.arg('--django-skip-inject-db',
        action='store_false',
        help='(django flavor) don\'t inject database settings')
@utils.arg('--django-settings',
        default="settings",
        help='(django flavor) the django settings path')
@utils.arg('--wsgi-entry',
        default="app:entry",
        help='(wsgi flavor) the entrypoint of the application')
def create(self, args):
    """Create a new resource."""

    values = vars(args)
    values.pop('func')

    if args.type == "app":
        environment = {
                    "requirements_file": "requirements.txt",
                    "cname_records": [],
                    "name": args.environment,
                    "backends": [
                        {
                            "count": 1,
                            "region": "eu1"
                        }
                    ],
                    "flavor": args.flavor,
                    }
        message = {
                "environments": [environment],
                "name": args.name,
                "repository": {
                    "location": args.location,
                    "name": args.environment,
                    "variant": "git"
                    },
                "variant": "python"
                }
        if args.flavor == "wsgi":
            message["environment"] = {
                    "wsgiflavor": {
                        "wsgi_project_root": args.root,
                        "wsgi_entry_point": args.wsgi_entry
                        }
                    }
        elif args.flavor == "django":
            message["environment"] = {
                    "djangoflavor": {
                        "django_project_root": args.root,
                        "django_settings_module": args.django_settings,
                        "inject_db": args.django_skip_inject_db
                        }
                    }
    elif args.type == "repository":
        message = {
                "name": args.name,
                "location": args.location,
                "variant": "git"
                }

    url = "%s/%s/" % (args.base_url, args.type)
    context = {"username": args.username, "password": args.password}
    try:
        response = request(
                url,
                method='POST',
                message=json.dumps(message),
                context=context)
    except:
        pass

    if response.status_code in range(200, 204) :
        sys.stdout.write("%s %s created" % (
            args.type.capitalize(), args.name))
    elif response.status_code == 405:
        sys.stderr.write("%s %s already exists" % (
            args.type.capitalize(), args.name))
    elif response.status_code < 500:
        sys.stderr.write("Something went wrong...")
