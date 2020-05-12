import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Union

TRIALS_ROOT = 'final_results/trials'
OUT_ROOT = 'final_results/collated'
RADII = {'inner': 120, 'outer': 200}

def main():

    df = concat_all_trajs(TRIALS_ROOT)
    ring_df = extract_ring(df.copy(), RADII, relative=False)
    show_ring(df, ring_df, OUT_ROOT, RADII, relative=False)
    
    save_collated(df, OUT_ROOT, 'all')
    save_collated(ring_df, OUT_ROOT, 'ring')
    
    add_rel_distances(df)
    ring_df = extract_ring(df.copy(), RADII, relative=True)
    show_ring(df, ring_df, OUT_ROOT, RADII, relative=True)

def extract_ring(df: pd.DataFrame, radii: dict, relative=False) -> pd.DataFrame:
    """Extract data from within the N-ring by dropping outlying rows.

    Args:
        df: DataFrame containing all of the trial data.
        radii: Inner and outer radii of N-ring.
        relative: Computes radii with relative distances if True

    Returns:
        DataFrame that only contains data that lies within the N-ring.
    """
    
    outer_rad, inner_rad = extract_radii(radii)

    if relative is False:
        df['R_1'] = (df['X_1'] ** 2 + df['Y_1'] ** 2) ** (1/2.)
        df['R_2'] = (df['X_2'] ** 2 + df['Y_2'] ** 2) ** (1/2.)
        
        df.drop(df[df.R_1 > outer_rad].index, inplace=True)
        df.drop(df[df.R_1 < inner_rad].index, inplace=True)

        df.drop(df[df.R_2 > outer_rad].index, inplace=True)
        df.drop(df[df.R_2 < inner_rad].index, inplace=True)

    else:
        df['R'] = (df['rel_X'] ** 2 + df['rel_Y'] ** 2) ** (1/2.)

        df.drop(df[df.R > outer_rad].index, inplace=True)
        df.drop(df[df.R < inner_rad].index, inplace=True)

    return df
    
def extract_radii(radii: dict) -> Union[float, float]:
    """Extract inner and outer radii from dict.
    
    Args:
        radii: Dictionary with inner and outer radii.
    """
    
    return radii['outer'], radii['inner']
    
def add_rel_distances(df: pd.DataFrame):
    """Compute relative distances between the airplanes.

    Args:
        df: DataFrame containing all trial trajectories.
    """
    
    df['rel_X'] = df['X_1'] - df['X_2']
    df['rel_Y'] = df['Y_1'] - df['Y_2']

def save_collated(df: pd.DataFrame, root: str, fname: str):
    """Save collated data to output directory.

    Args:
        df: DataFrame containing data from all of the trials.
        root: Root output directory where we want to save data.
        fname: Filename prefix for saved data.
    """

    all_states = df[['X_1', 'Y_1', 'Theta_1', 'X_2', 'Y_2', 'Theta_2']].to_numpy()
    all_actions = df[['V_1', 'W_1', 'V_2', 'W_2']].to_numpy()

    np.save(os.path.join(root, fname + '-states.npy'), all_states)
    np.save(os.path.join(root, fname + '-actions.npy'), all_actions)

def concat_all_trajs(root: str) -> pd.DataFrame:
    """Create DataFrames from saved np trials.

    Args:
        root: Root directory of saved trial files.

    Returns:
        DataFrame containing all of the trial data.
    """

    frames = []
    for name in os.listdir(root):
        print(f'Loading data from {name.capitalize()} -> ', end='')
        trial_dirs = os.listdir(os.path.join(root, name))

        for idx in range(len(trial_dirs)):
            full_path = os.path.join(root, name, name + f'-{idx + 1}')
            states = np.load(os.path.join(full_path, 'all_states.npy'))
            actions = np.load(os.path.join(full_path, 'all_actions.npy'))

            state_df = pd.DataFrame(data=states, columns=['X_1', 'Y_1', 'Theta_1', 'X_2', 'Y_2', 'Theta_2'])
            action_df = pd.DataFrame(data=actions, columns=['V_1', 'W_1', 'V_2', 'W_2'])

            num_pts = states.shape[0]
            data = list(zip(
                [name for _ in range(num_pts)],
                [idx + 1 for _ in range(num_pts)],
                range(num_pts)
            ))
            info_df = pd.DataFrame(data=data, columns=['Name', 'Trial', 'Trial_index'])

            sim_df = pd.concat([info_df, state_df, action_df], axis=1)
            frames.append(sim_df)

        print(f'found {idx + 1} trajectories.')

    return pd.concat(frames, ignore_index=True)

def show_ring(df: pd.DataFrame, ring_df: pd.DataFrame, root: str, radii: dict, 
              relative=False):
    """Plot all of the trials in collated and ring DataFrames.

    Args:
        df: DataFrame containing all of the trial data.
        ring_df: DataFrame containing all of the trial data within the N-ring.
        root: Root directory where we want to save the plot.
        radii: Dictionary with inner and outer radii of N-ring.
        relative: Plots relative distances if True.
    """
    
    sns.set(style='darkgrid')
    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(1, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    plot_all_trajs(ax1, df, radii, relative=relative)
    ax1.set_title('All trajectories')

    ax2 = fig.add_subplot(gs[0, 1])
    plot_all_trajs(ax2, ring_df, radii, plot_rings=True, relative=relative)
    ax2.set_title('Ring trajectories')

    fig.suptitle('Expert trajectories')

    fname = 'expert-traj.png' if relative is False else 'rel-expert-traj.png'
    plt.savefig(os.path.join(root, fname))

def plot_all_trajs(ax: plt.axis, df: pd.DataFrame, radii: dict, 
                   plot_rings=False, relative=False):
    """Plot all of the trajectories in the input DataFrame on the given axis.

    Args:
        ax: Matplotlib axis on which we want to plot.
        df: DataFrame containing trajectory data.
        radii: Dictionary with inner and outer radii of N-ring.
        plot_rings: Boolean flag that plots outer and inner circles of N-ring if True.
    """

    cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True)
    outer_rad, inner_rad = extract_radii(radii)
    kwargs = {'data': df, 'legend': False, 'palette': cmap, 'edgecolor': None, 's': 20}
    
    if relative is False:
        ax = sns.scatterplot(x='X_1', y='Y_1', hue='Trial', **kwargs)
        sns.scatterplot(x='X_2', y='Y_2', hue='Trial', **kwargs)
    else:
        ax = sns.scatterplot(x='rel_X', y='rel_Y', hue='Trial', **kwargs)                    

    if plot_rings is True:
            
        outer_circle = plt.Circle((0, 0), outer_rad, color='blue', fill=False)
        ax.add_artist(outer_circle)

        inner_circle = plt.Circle((0, 0), inner_rad, color='blue', fill=False)
        ax.add_artist(inner_circle)

    ax.axis('equal')
    # ax.set_xlim([-2.0, 2.0])
    # ax.set_ylim([-2.0, 2.0])
    ax.set_xlabel('relative x position' if relative is True else 'x position')
    ax.set_ylabel('relative y position' if relative is True else 'y position')



if __name__ == '__main__':
    main()
