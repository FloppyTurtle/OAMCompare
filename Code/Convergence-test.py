"""
This is a typical input script that runs a simulation of
laser-wakefield acceleration using FBPIC.

Usage
-----
- Modify the parameters below to suit your needs
- Type "python lwfa_script.py" in a terminal

Help
----
All the structures implemented in FBPIC are internally documented.
Enter "print(fbpic_object.__doc__)" to have access to this documentation,
where fbpic_object is any of the objects or function of FBPIC.
"""

# -------
# Imports
# -------
import numpy as np
import sys
from scipy.constants import c, e, m_e
# Import the relevant structures in FBPIC
from fbpic.main import Simulation
from fbpic.lpa_utils.laser import add_laser_pulse

from fbpic.lpa_utils.laser.laser_profiles import LaguerreGaussLaser
from fbpic.openpmd_diag import FieldDiagnostic, ParticleDiagnostic, \
    set_periodic_checkpoint, restart_from_checkpoint

# ----------
# Parameters
# ----------
# Whether to use the GPU
use_cuda = False

# Order of the stencil for z derivatives in the Maxwell solver.
# Use -1 for infinite order, i.e. for exact dispersion relation in
# all direction (advice for single-GPU/single-CPU simulation).
# Use a positive number (and multiple of 2) for a finite-order stencil
# (required for multi-GPU/multi-CPU with MPI). A large `n_order` leads
# to more overhead in MPI communications, but also to a more accurate
# dispersion relation for electromagnetic waves. (Typically,
# `n_order = 32` is a good trade-off.)
# See https://arxiv.org/abs/1611.05712 for more information.
n_order = -1

# The simulation box
Nz =  int(sys.argv[2])  # Number of grid points along z
zmax = 30.e-6  # Right end of the simulation box (meters)
zmin = -30.e-6  # Left end of the simulation box (meters)
Nr = int(sys.argv[1])  # Number of grid points along r
rmax = 20.e-6  # Length of the box along r (meters)
m = 1            #
Nm = abs(m) + 1  # Number of modes used

# The simulation timestep
dt = (zmax - zmin) / Nz / c  # Timestep (seconds)

# The particles
p_zmin = 30.e-6  # Position of the beginning of the plasma (meters)
p_zmax = 500.e-6  # Position of the end of the plasma (meters)
p_rmax = 18.e-6  # Maximal radial position of the plasma (meters)
n_e = 4.e18 * 1.e6  # Density (electrons.meters^-3)
p_nz = 2  # Number of particles per cell along z
p_nr = 2  # Number of particles per cell along r
p_nt = 4  # Number of particles per cell along theta

# The moving window
v_window = c  # Speed of the window

# The diagnostics and the checkpoints/restarts
diag_period = 25  # Period of the diagnostics in number of timesteps
save_checkpoints = False  # Whether to write checkpoint files
checkpoint_period = 100  # Period for writing the checkpoints
use_restart = False  # Whether to restart from a previous checkpoint
track_electrons = True  # Whether to track and write particle ids

# The density profile
ramp_start = 30.e-6
ramp_length = 40.e-6


def dens_func(z, r):
    """Returns relative density at position z and r"""
    # Allocate relative density
    n = np.ones_like(z)
    # Make linear ramp
    n = np.where(z < ramp_start + ramp_length, (z - ramp_start) / ramp_length, n)
    # Supress density before the ramp
    n = np.where(z < ramp_start, 0., n)
    return n


# The interaction length of the simulation (meters)
L_interact = 50.e-6  # increase to simulate longer distance!
# Interaction time (seconds) (to calculate number of PIC iterations)
T_interact = 365.e-15
# T_interact = ( L_interact + (zmax-zmin) ) / v_window
# (i.e. the time it takes for the moving window to slide across the plasma)

# ---------------------------
# Carrying out the simulation
# ---------------------------

# NB: The code below is only executed when running the script,
# (`python lwfa_script.py`), but not when importing it (`import lwfa_script`).
if __name__ == '__main__':

    # Initialize the simulation object
    sim = Simulation(Nz, zmax, Nr, rmax, Nm, dt, zmin=zmin,
                     n_order=n_order, use_cuda=use_cuda,
                     boundaries={'z': 'open', 'r': 'reflective'})
    # 'r': 'open' can also be used, but is more computationally expensive

    # Create the plasma electrons
    elec = sim.add_new_species(q=-e, m=m_e, n=n_e,
                               dens_func=dens_func, p_zmin=p_zmin, p_zmax=p_zmax, p_rmax=p_rmax,
                               p_nz=p_nz, p_nr=p_nr, p_nt=p_nt)

    # Load initial fields
    # Create a Gaussian laser profile
    # The laser
    a0 = 203.e-2  # Laser amplitude
    w0 = 30.e-7  # Laser waist
    tau = 20.e-15  # Laser duration
    z0 = 15.e-6  # Laser centroid

    from fbpic.lpa_utils.laser.laser_profiles import GaussianLaser
    laser_profile = GaussianLaser(a0, w0, tau, z0, zf=ramp_start )

    # Add the laser to the fields of the simulation
    add_laser_pulse(sim, laser_profile)

    # Circularly polarised (their example)
    # from fbpic.lpa_utils.laser.laser_profiles import GaussianLaser
    # linear_profile1 = GaussianLaser( a0/math.sqrt(2), w0, tau, z0,
    #                         theta_pol=0., cep_phase=0.)
    # linear_profile2 = GaussianLaser( a0/math.sqrt(2), w0, tau, z0,
    #                         theta_pol=math.pi/2, cep_phase=math.pi/2 )

    # circular_profile = linear_profile1 + linear_profile2
    # add_laser_pulse( sim, circular_profile )

    # from fbpic.lpa_utils.laser import DonutLikeLaguerreGaussLaser
    # donut_laser_profile = DonutLikeLaguerreGaussLaser(0, 1, a0, w0, tau, z0, zf=ramp_start, lambda0=815.e-9)
    # p  m  amp waist duration centroid focal plane
    # add_laser_pulse(sim, donut_laser_profile)

    #LagGauss_laser_profile = LaguerreGaussLaser(0, m, a0, w0, tau, z0, zf=ramp_start, lambda0=815.e-9)
    # p  m  amp waist duration centroid focal plane
    #add_laser_pulse(sim, LagGauss_laser_profile)

    if use_restart is False:
        # Track electrons if required (species 0 correspond to the electrons)
        if track_electrons:
            elec.track(sim.comm)
    else:
        # Load the fields and particles from the latest checkpoint file
        restart_from_checkpoint(sim)

    # Configure the moving window
    sim.set_moving_window(v=v_window)

    # Add diagnostics
    sim.diags = [FieldDiagnostic(diag_period, sim.fld, comm=sim.comm),
                 ParticleDiagnostic(diag_period, {"electrons": elec},
                                    select={"uz": [1.0, None]}, comm=sim.comm,
                                    particle_data=["gamma", "position", "weighting"])]

    # Add checkpoints
    if save_checkpoints:
        set_periodic_checkpoint(sim, checkpoint_period)

    # Number of iterations to perform
    N_step = int(T_interact / sim.dt)

    # Run the simulation
    sim.step(1000)
    print('')
