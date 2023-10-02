import h5py as h5
import openpmd_api as io
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from openpmd_viewer import OpenPMDTimeSeries

#h5.run_tests()

if __name__ == "__main__":
    sliceNum = 1
    cwd = os.getcwd()
    path =  cwd + "\\diags\\hdf5"
    files = os.listdir(path)
    series = io.Series(".\\diags\\hdf5\\data%T.h5",io.Access.read_only)   ## Create a file series to process

    print("Series",str(series.openPMD))
    
    ## Print iteration number and related file
    print("The Series contains {0} iterations:".format(len(series.iterations)))
    for i in series.iterations:
        print("\t {0}".format(i))
    print("")

    ## Print particle attributes
    p = series.iterations[0]
    for ps in p.particles:
        print("\t {0}".format(ps))
        print("With records:")
        for r in series.iterations[0].particles[ps]:
            print("\t {0}".format(r))

    ## For each file process the data
    print(series.iterations[100])
    for val in series.iterations:
        i = series.iterations[val]

        E_z_modes = i.meshes["E"]["z"]
        shape = E_z_modes.shape  # (modal components, r, z)

        E_z_raw = E_z_modes[:, :, :]

        """ # read E_z in mode_0 (one scalar field)
        E_z_m0 = E_z_modes[0:1, 0:shape[1], 0:shape[2]]
        # read E_z in mode_1 (two fields; skip mode_0 with one scalar field)
        E_z_m1 = E_z_modes[1:3, 0:shape[1], 0:shape[2]]
        
        """
        toCylindrical      = io.thetaMode.toCylindrical(modes="all")
        toCylindricalSlice = io.thetaMode.toCylindricalSlice(theta_radian=1.5708, modes="all") 

        # reconstruction to 2D slice in cylindrical coordinates (r, z) for a fixed theta

        E_z_90deg = toCylindricalSlice(E_z_modes)[:, :]
        E_r_90deg = toCylindricalSlice(i.meshes["E"]["r"])[:, :]
        E_t_90deg = toCylindricalSlice(i.meshes["E"]["t"])[:, :]
        # reconstruction to 3D cylindrical coordinates (r, t, z)
        E_z_cyl = toCylindrical(E_z_modes)[:, :, :]
        # series.flush()

        # reconstruction to 3D and 2D cartesian: E_x, E_y, E_z
        toCartesian        = io.thetaMode.toCartesian(discretize={'x': 1.e-6, 'y': 1.e-6}, modes="all")
        toCartesianSliceYZ = io.thetaMode.toCartesianSlice(discretize={'x': 1.e-6, 'y': 1.e-6}, slice_dir='x',slice_rel=0., modes="all")
        # and absolute slice position
        E_z_xyz = toCartesian(E_z_modes)[:, :, :]      # (x, y, z)
        E_z_yz  = toCartesianSliceYZ(E_z_modes)[:, :]  # (y, z)

        ax = plt.figure().add_subplot(projection='3d')
        X, Y, Z = axes3d.get_test_data(0.05)

        # Plot the 3D surface
        ax.plot_surface(X, Y, Z, edgecolor='royalblue', lw=0.5, rstride=8, cstride=8,
                        alpha=0.3)

        # Plot projections of the contours for each dimension.  By choosing offsets
        # that match the appropriate axes limits, the projected contours will sit on
        # the 'walls' of the graph.
        ax.contour(X, Y, Z, zdir='z', offset=-100, cmap='coolwarm')
        ax.contour(X, Y, Z, zdir='x', offset=-40, cmap='coolwarm')
        ax.contour(X, Y, Z, zdir='y', offset=40, cmap='coolwarm')

        ax.set(xlim=(-40, 40), ylim=(-40, 40), zlim=(-100, 100), xlabel='X', ylabel='Y', zlabel='Z')
        plt.show()
        series.flush()

    series.close()