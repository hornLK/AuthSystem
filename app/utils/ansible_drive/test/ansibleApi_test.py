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
from ansible.template import Templar
from ansible.vars.hostvars import HostVars
from ansible.playbook.play_context import PlayContext
from ansible.executor.task_result import TaskResult
from ansible.executor.play_iterator import PlayIterator
from ansible.plugins.loader import callback_loader, strategy_loader, module_loader
from ansible.vars.reserved import warn_if_reserved

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
        return {host:res}
"""
class LkTaskQueueManager(TaskQueueManager):
    def __init__(self, inventory, variable_manager, loader, options, passwords,
                    stdout_callback=None, run_additional_callbacks=True,
                    run_tree=False):
        self._tasks_result = {}
        super(LkTaskQueueManager,self).__init__(inventory, variable_manager,
                                                loader, options, passwords,
                                                stdout_callback=None,
                                                run_additional_callbacks=True,
                                                run_tree=False)
    def run(self, play):
        '''
        Iterates over the roles/tasks in a play, using the given (or default)
        strategy for queueing tasks. The default is the linear strategy, which
        operates like classic Ansible by keeping all hosts in lock-step with
        a given task (meaning no hosts move on to the next task until all hosts
        are done with the current task).
        '''

        if not self._callbacks_loaded:
            self.load_callbacks()

        all_vars = self._variable_manager.get_vars(play=play)
        warn_if_reserved(all_vars)
        templar = Templar(loader=self._loader, variables=all_vars)

        new_play = play.copy()
        new_play.post_validate(templar)
        new_play.handlers = new_play.compile_roles_handlers() + new_play.handlers

        self.hostvars = HostVars(
            inventory=self._inventory,
            variable_manager=self._variable_manager,
            loader=self._loader,
        )

        play_context = PlayContext(new_play, self._options, self.passwords, self._connection_lockfile.fileno())
        for callback_plugin in self._callback_plugins:
            if hasattr(callback_plugin, 'set_play_context'):
                callback_plugin.set_play_context(play_context)

        play_res  = self.send_callback('v2_playbook_on_play_start', new_play)
        # initialize the shared dictionary containing the notified handlers
        self._initialize_notified_handlers(new_play)

        # build the iterator
        iterator = PlayIterator(
            inventory=self._inventory,
            play=new_play,
            play_context=play_context,
            variable_manager=self._variable_manager,
            all_vars=all_vars,
            start_at_done=self._start_at_done,
        )

        # adjust to # of workers to configured forks or size of batch, whatever is lower
        self._initialize_processes(min(self._options.forks, iterator.batch_size))

        # load the specified strategy (or the default linear one)
        strategy = strategy_loader.get(new_play.strategy, self)
        if strategy is None:
            raise AnsibleError("Invalid play strategy specified: %s" % new_play.strategy, obj=play._ds)

        # Because the TQM may survive multiple play runs, we start by marking
        # any hosts as failed in the iterator here which may have been marked
        # as failed in previous runs. Then we clear the internal list of failed
        # hosts so we know what failed this round.
        for host_name in self._failed_hosts.keys():
            host = self._inventory.get_host(host_name)
            iterator.mark_host_failed(host)

        self.clear_failed_hosts()

        # during initialization, the PlayContext will clear the start_at_task
        # field to signal that a matching task was found, so check that here
        # and remember it so we don't try to skip tasks on future plays
        if getattr(self._options, 'start_at_task', None) is not None and play_context.start_at_task is None:
            self._start_at_done = True

        # and run the play using the strategy and cleanup on way out
        play_return = strategy.run(iterator, play_context)

        # now re-save the hosts that failed from the iterator to our internal list
        for host_name in iterator.get_failed_hosts():
            self._failed_hosts[host_name] = True

        strategy.cleanup()
        self._cleanup_processes()
        return self._tasks_result

    def send_callback(self, method_name, *args, **kwargs):
        for callback_plugin in [self._stdout_callback] + self._callback_plugins:
            # a plugin that set self.disabled to True will not be called
            # see osx_say.py example for such a plugin
            if getattr(callback_plugin, 'disabled', False):
                continue
            # send clean copies
            new_args = []
            for arg in args:
                # FIXME: add play/task cleaners
                if isinstance(arg, TaskResult):
                    temp_dict ={str(arg._task):arg._result,
                     "is_failed":arg.is_failed(),
                     'is_skipped':arg.is_skipped(),
                     'is_unreachable':arg.is_unreachable()}
                    if self._tasks_result.get(arg._host,None):
                        self._tasks_result[str(arg._host)].append(temp_dict)
                    else:
                        self._tasks_result[str(arg._host)] = []
                        self._tasks_result[str(arg._host)].append(temp_dict)
                    new_args.append(arg.clean_copy())
                # elif isinstance(arg, Play):
                # elif isinstance(arg, Task):
                else:
                    new_args.append(arg)
def main():
    api_key = "0a37511d-be7d-4fdd-ab17-28b6c659d763"
    url = "http://192.168.220.3:8890/apiv1/auths/host/list/"

    Options = namedtuple('Options', ['connection', 'module_path', 'forks',
                                     'become', 'become_method', 'become_user',
                                     'check',
                                     'diff','remote_user','private_key_file'])
    # initialize needed objects
    loader = DataLoader()
    options = Options(connection="smart", module_path=['/path/to/mymodules'], forks=100, become=None, become_method=None, become_user=None, check=False,
                  diff=False,remote_user="kk",private_key_file='/data/MzIDCManage/MzManage/utils/ansible_drive/test/id_rsa')
    passwords = {}
# Instantiate our ResultCallback for handling results as they come in
    #results_callback = ResultCallback()

# create inventory and pass to var manager
# use path to host config file as source or hosts in a comma separated string
    inventory = InventoryManager(loader=loader,
                                 sources=inventory_list(url,api_key)+"192.168.220.4")
    variable_manager = VariableManager(loader=loader, inventory=inventory)

# create play with tasks
    play_source =  dict(
            name = "Ansible Play",
            hosts = ['localhost','192.168.220.3','192.168.220.4'],
            gather_facts = 'no',
            roles = [
                dict(name="SyncJumpserverUserKeys",vars={"username":"liukaiqiang"})
         ]
        )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    # actually run it
    tqm = None
    try:
        tqm = LkTaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                 loader=loader,
                 options=options,
                 passwords=passwords,
                #stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
                stdout_callback=None,  # Use our custom callback instead of the ``default`` callback plugin
            )
        result = tqm.run(play)
        print(json.dumps(result))
        return json.dumps(result)
    except Exception as e:
        print(e)
    finally:
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

if __name__ == "__main__":
    main()


