import json
import requests,time,hashlib
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

"""
def inventory_list(url,api_key):
    SECRET_API_KEY = api_key
    time_span = time.time()
    secret_data = "%s|%f" % (SECRET_API_KEY,time_span)
    hash_obj = hashlib.md5(secret_data.encode("utf-8"))
    encryption = hash_obj.hexdigest()
    send_data = encryption+"|"+str(time_span)
    headers = {'content-type':
                'application/json',"X-Http-Secretkey":send_data}
    res = requests.get(url,headers=headers)
    dict_json = [host.get("hostIP") for host in json.loads(res.text)]
    re_str = ",".join(dict_json)
    return re_str
"""
class ResultCallback(CallbackBase):
    def runner_on_ok(self,host,res):
        print(json.dumps({host:res},indent=4))
    """
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))
    """

def runner(connection,hosts,roles):
    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
    # initialize needed objects
    loader = DataLoader()
    options = Options(connection='192.168.220.3', module_path=['/path/to/mymodules'], forks=100, become=None, become_method=None, become_user=None, check=False,
                  diff=False)
    passwords = dict(vault_pass='123123')

    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    # use path to host config file as source or hosts in a comma separated string
    inventory = InventoryManager(loader=loader, sources=",".join(hosts))
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # create play with tasks
    play_source =  dict(
        name = "Ansible Play",
        hosts = ['localhost','192.168.220.3'],
        gather_facts = 'no',
        roles = roles
    )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    print("----------------------")
    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
            )
        result = tqm.run(play)
    except Exception as e:
        print(e)
    finally:
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
