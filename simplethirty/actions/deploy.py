import json
import sys


from simplethirty import utils
from libthirty.state import env
from libthirty.actions import ActionHandler
from libthirty.exceptions import HttpReturnError


##
# Deploy app resources
##
@utils.arg('name',
    default=None,
    help="The name of the resource to create.")
@utils.arg('--environment',
    default='production',
    help="The name of the environment to deploy.")
def deploy(args):
    """Deploy an app resource."""
    cmd = {'action': 'deploy', 'options': {}}
    cmd['options']['environment'] = args.environment

    env.account = args.account
    env.label = 'app'
    env.resource = args.name
    env.username = args.username
    env.password = args.password

    action = ActionHandler(**cmd)

    try:
        # Lets queue the action
        action.queue()
    except HttpReturnError as e:
        #FIXME: push this into its own formatting method
        error = {
                "code": e[0],
                "message": e[1]
                }
        sys.stderr.write(json.dumps(error, indent=4))
        sys.stderr.flush()
        sys.exit(1)

    if action.response.status_code >= 500:
        sys.stderr.write(action.response.content)
        sys.stderr.flush()
        sys.exit(1)

    try:
        utils._poll_logbook(action.uuid)
    except KeyboardInterrupt:
        sys.exit(1)
    except HttpReturnError as e:
        #FIXME: push this into its own formatting method
        error = {
                "code": e[0],
                "message": e[1]
                }
        sys.stderr.write(json.dumps(error, indent=4))
        sys.stderr.flush()
        sys.exit(1)

    sys.stdout.flush()
