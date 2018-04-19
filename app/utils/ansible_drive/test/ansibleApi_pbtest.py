import json
from ansible import constants as C
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.ssh_functions import check_for_controlpersist
from ansible.plugins.callback import CallbackBase

def inventory_list(url,api_key):
    SECRET_API_KEY = api_key
    time_span = time.time()
    secret_data = "%s|%f" % (SECRET_API_KEY,time_span)
    hash_obj = hashlib.md5(secret_data.encode("utf-8"))
    encryption = hash_obj.hexdigest()
    send_data = encryption+"|"+str(time_span)
    headers = {'content-type':'application/json',"X-Http-Secretkey":send_data}
    res = requests.get(url,headers=headers)
    dict_json = [host.get("hostIP") for host in json.loads(res.text)]
    re_str = ",".join(dict_json)
    return re_str

loader = DataLoader()

api_key = "0a37511d-be7d-4fdd-ab17-28b6c659d763"
url = "http://192.168.220.3:8890/apiv1/auths/host/list/"

Options = namedtuple('Options', ['connection', 'module_path', 'forks',
                                 'become', 'become_method', 'become_user',
                                 'check', 'diff'])

options = Options(connection='192.168.220.3',
                  module_path=['/path/to/mymodules'], forks=100, become=None,
                  become_method=None, become_user=None, check=False,
                  diff=False)

passwords = dict(vault_pass='123123')

results_callback = ResultCallback()

class ResultCallback():
    def v2_playbook_on_start(self,playbook):
        print(playbook)
        print(dir(playbook))

class LkPlaybookExecutor(PlaybookExecutor):

    def __init__(self,playbooks,inventory,variable_manager,loader,options,passwords,stdout_callback=None):
        self._stdout_callback=stdout_callback
        super(LkPlaybookExecutor,self).__init__(playbooks, inventory,
                                                variable_manager, loader,
                                                options, passwords)

