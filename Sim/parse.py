import numpy as np
import json
import os
import shutil
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d as interp
import argparse

from Trajectory import Trajectory

ROOT = './simulator/data'
OUT_DIR = './final_results/trials'

# Configuration for Haimin's simulation
ORIG_CONFIG = {
    'speed': {'min': 0.1, 'max': 1.0},
    'ang_speed': {'min': -1.0, 'max': 1.0},
    'world_size': {'x_low': -2.0, 'x_high': 2.0, 'y_low': -1.0, 'y_high': 1.0}
}

def main(args):

    if len(os.listdir(ROOT)) == 0:
        raise Exception('You must run a simulation before parsing data.')

    # load simulation configuration file
    config = load_json('config')
    config = concat_config([ORIG_CONFIG, config], keys=['python', 'javascript'])

    # load trajectory from file and map states and actions
    traj_A1 = extract_traj('airplane1', config)
    traj_A2 = extract_traj('airplane2', config)

    all_states = np.hstack((traj_A1.states, traj_A2.states))
    np.save(os.path.join(ROOT, 'all_states.npy'), all_states)

    all_actions = np.hstack((traj_A1.actions, traj_A2.actions))
    np.save(os.path.join(ROOT, 'all_actions.npy'), all_actions)

    plot_traj(ROOT, trajs=[traj_A1, traj_A2], config=config)
    move_to_final_dir(args, ROOT, OUT_DIR)

def plot_traj(root: str, trajs: list, config: dict):
    """Plots trajectories from a list of trajectories.

    Args:
        root: Root directory to save figure to.
        trajs: List of Trajectory instances.
        config: Configuration file for simulation.
    """

    fig, ax = plt.subplots()

    for t in trajs:
        line = ax.plot(t.states[:, 0], t.states[:, 1], label=t.name)
        launch = plt.Circle(t.states[0, :2], 0.05, color=line[0].get_color())
        ax.add_artist(launch)

    center = plt.Circle((0, 0), config['javascript']['center_radius'], color='r')
    ax.add_artist(center)

    ax.legend()
    ax.grid()
    ax.axis('equal')
    
    js_world = config['javascript']['world_size']
    ax.set_xlim(-1. * js_world['x'] / 2., js_world['x'] / 2.)
    ax.set_ylim(-1. * js_world['y'] / 2., js_world['y'] / 2.)
    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    plt.savefig(os.path.join(ROOT, 'trajectories.png'))

def move_to_final_dir(args: dict, root: str, out_dir: str):
    """Move all of the data from one trial to <out_dir>/<name>/<name-id> where id
    specifies the total number of trials user <name> has added.

    Args:
        args: Command line arguments.
        root: Root directory where data is currently saved from simulation.
        out_dir: Output base directory where we want to move data to.
    """

    def create_dir(n: int) -> str:
        """Create directory <out_dir>/<name>/<name-{n + 1}>.

        Args:
            n: Number of trajectories <name> has added so far.

        Returns:
            name_dir: Name of directory created.
        """

        name_dir = os.path.join(out_dir, args.name, args.name + f'-{n + 1}')
        os.makedirs(name_dir)

        return name_dir

    if os.path.exists(os.path.join(out_dir, args.name)) is True:
        name_dirs = os.listdir(os.path.join(out_dir, args.name))
        num_dirs = len([d for d in name_dirs if d.startswith(args.name)])
        write_dir = create_dir(num_dirs)

    else:
        write_dir = create_dir(0)

    data_files = os.listdir(root)
    for f in data_files:
        shutil.move(os.path.join(root, f), write_dir)


def extract_traj(fname: str, config: dict) -> Trajectory:
    """Extract trajector from filename and create Trajectory instance.

    Args:
        fname: Filename from which to load trajectory.
        config: Dictionary containing parameters of javascript simulation.

    Returns:
        Trajectory with mapped states and actions.
    """

    states, actions = [], []
    data = load_json(fname)

    for step in data:
        states.append(step['data']['state'])
        actions.append(step['data']['action'])

    traj = Trajectory(states, actions, config, fname)
    traj.remap_states()        
    traj.as_numpy()

    return traj

def load_json(fname: str) -> list:
    """Load JSON file from filename.

    Args:
        fname: Filename from which to load trajectory.

    Returns:
        Data from simulation loaded as python list.
    """

    with open(os.path.join(ROOT, fname + '.json')) as f:
        data = json.load(f)

    return data

def concat_config(confs: list, keys: list) -> dict:
    """Concatenate config files from python and javascript.

    Args:
        configs: List of configuration dictionaries.
        keys: List of strings specifying keys for new dictionary.

    Return:
        Dictionary with both configs.
    """

    return {key: conf for (key, conf) in zip(keys, confs)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True, help='Your name')
    args = parser.parse_args()

    main(args)
