class StateMachine(object):
    def __init__(self):
        self.states = {}
        self.active_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def think(self, time_passed):
        if self.active_state is None:
            return
        self.active_state.do_actions()

        new_state_name = self.active_state.check_conditions(time_passed)
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()


class State(object):

    def __init__(self, name):
        self.name = name

    def do_actions(self):
        pass

    def check_conditions(self, time_passed):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
