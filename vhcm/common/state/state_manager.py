from vhcm.models.system_state import SystemStates
from vhcm.common.singleton import Singleton
from vhcm.common.dao.model_query import is_table_exists


class StateManager(object, metaclass=Singleton):
    def __init__(self):
        self.states = None
        # Only load setting when project did its first migration
        if is_table_exists('system_states'):
            self.states = SystemStates.objects.all()

    def get_state(self, name):
        model = self.states.filter(name=name).first()
        if model:
            return model.state
        else:
            return None


# Instance
state_manager = StateManager()
