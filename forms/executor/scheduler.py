#  Copyright 2022-2023 The FormS Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from enum import Enum, auto
from forms.executor.executionnode import *
from forms.executor.utils import ExecutionConfig, ExecutionContext
from forms.utils.exceptions import SchedulerNotSupportedException


class BaseScheduler(ABC):
    def __init__(self, exec_config: ExecutionConfig, execution_tree: ExecutionNode):
        self.exec_config = exec_config
        self.execution_tree = execution_tree

    @abstractmethod
    def next_subtree(self) -> (ExecutionNode, list):
        pass

    @abstractmethod
    def finish_subtree(self, execution_subtree: ExecutionNode, result_node: RefExecutionNode):
        pass

    def is_finished(self) -> bool:
        return isinstance(self.execution_tree, RefExecutionNode)

    def get_results(self) -> Table:
        assert isinstance(self.execution_tree, RefExecutionNode)
        return self.execution_tree.table


class SimpleScheduler(BaseScheduler):
    def next_subtree(self) -> (ExecutionNode, list):
        cores = self.exec_config.cores
        num_of_formulae = self.exec_config.num_of_formulae
        exec_subtree_list = [self.execution_tree.replicate_subtree() for _ in range(cores)]
        exec_context_list = [
            ExecutionContext(i * num_of_formulae / cores, (i + 1) * num_of_formulae / cores)
            for i in range(cores)
        ]
        for i in range(cores):
            exec_subtree_list[i].set_exec_context(exec_context_list[i])
        return self.execution_tree, exec_subtree_list

    def finish_subtree(self, execution_subtree: ExecutionNode, result_table: Table):
        self.execution_tree = create_intermediate_ref_node(result_table, execution_subtree)


class Scheduler(Enum):
    SIMPLE = auto()


scheduler_class_dict = {Scheduler.SIMPLE.name.lower(): SimpleScheduler}


def create_scheduler_by_name(s_name: str, exec_config: ExecutionConfig, execution_tree: ExecutionNode):
    if s_name in scheduler_class_dict:
        scheduler_class_dict[s_name](exec_config, execution_tree)
    raise SchedulerNotSupportedException(f"Scheduler {s_name} is not supported")