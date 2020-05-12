from scipy.interpolate import interp1d as interp
import numpy as np
import os

class Trajectory:
    def __init__(self, states: list, actions: list, config: dict, name: str):
        """Constructor for trajectory from airplane simulation.

        Args:
            states: List of states encountered by airplane.
            actions: List of actions taken by airplane.
            config: Simulation configuration dictionary.
            name
        """

        self._states = states
        self._actions = actions
        self._sim_config, self._py_config = config['javascript'], config['python']
        self._name = name

    def __repr__(self) -> str:
        """Representation string for trajectory class."""

        return f'Trajectory for {self._name}'

    @property
    def name(self):
        """Getter method for airplane name."""

        return self._name

    @property
    def states(self):
        """Getter method for airplane states."""

        return self._states

    @property
    def actions(self):
        """Getter method for airplane actions."""

        return self._actions

    def map_traj(self):
        """Maps state and action trajectories to correct range for learning.

        Modifies:
            self._actions and self._states are remapped.
        """

        self.remap_actions()
        self.remap_states()

    def as_numpy(self):
        """Turns states and actions into numpy array.

        Modifies:
            self._states and self._actions move to np.ndarrays.
        """

        self._states = np.array(self._states)
        self._actions = np.array(self._actions)

    def save(self, root: str):
        """Save states and actions to numpy files.

        Args:
            root: Root directory to save files to.

        Saves:
            Saves self._states and self._actions to .npy files.
        """

        np.save(os.path.join(root, self._name + '-states.npy'), self._states)
        np.save(os.path.join(root, self._name + '-actions.npy'), self._actions)

    @staticmethod
    def __clip(num: float, min_val, max_val):
        return max(min(num, max_val), min_val)

    def remap_actions(self):
        """Map actions to correct range for neural network.

        Modifies:
            self._actions values are mapped to a different range.
        """

        # shorten names for clarity
        js_speed, js_ang_speed = self._sim_config['speed'], self._sim_config['ang_speed']
        py_speed, py_ang_speed = self._py_config['speed'], self._py_config['ang_speed']

        # create maps to interpolate values
        speed_map = interp([js_speed['min'], js_speed['max']], [py_speed['min'], py_speed['max']])
        ang_speed_map = interp([js_ang_speed['min'], js_ang_speed['max']], [py_ang_speed['min'], py_ang_speed['max']])

        # loop through data to convert actions to correct range
        for idx, (vel, ang_vel) in enumerate(self._actions):
            vel = self.__clip(vel, min_val=js_speed['min'], max_val=js_speed['max'])
            ang_vel = self.__clip(ang_vel, min_val=js_ang_speed['min'], max_val=js_ang_speed['max'])
            self._actions[idx] = [float(speed_map(vel)), float(ang_speed_map(ang_vel))]

    def remap_states(self):
        """Map states to correct range for neural network.

        Modifies:
            self._states values are mapped to a different range.
        """

        js_world = self._sim_config['world_size']
        py_world = self._py_config['world_size']

        x_map = interp([0, js_world['x']], [-1. * js_world['x'] / 2., js_world['x'] / 2.])

        # reverse first argument since in JS, y values increase as you move down
        y_map = interp([js_world['y'], 0], [-1. * js_world['y'] / 2., js_world['y'] / 2.])

        for idx, (x, y, theta) in enumerate(self._states):
            self._states[idx] = [float(x_map(x)), float(y_map(y)), theta % (2 * np.pi)]
