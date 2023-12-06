import os, sys, numpy, pyvista, platform
import imageio.v2 as imageio
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm


class fbpic:
    def __init__(self, relativeInputPath="/diags/hdf5", savePath = "", norm=None) -> None:
        # Find what platform we are on necessary for saving files
        self.platform = platform.system()
        print("fbpic data object created.")
        print("Platform is {}".format(self.platform))
        if relativeInputPath == "/diags/hdf5":
            print("Default file path used, changing based on platform (Linux/Windows).")
            if self.platform == "Linux":
                relativeInputPath = "/diags/hdf5"
                print("Platform is Linux hence path is {}".format(relativeInputPath))
            elif self.platform == "Windows":
                relativeInputPath = "\\diags\\hdf5"
                print("Platform is Windows hence path is {}".format(relativeInputPath))


        # Get the data input path and set it
        self.cwd = os.getcwd()
        self.savePath = savePath
        self.inputDataPath = self.cwd + relativeInputPath
        self.relativeInputPath = relativeInputPath
        self.norm = norm
        self.ts = OpenPMDTimeSeries(self.inputDataPath)
        print("HDF5 series files found...")

        self.it = self.ts.iterations
        self.time_it = self.ts.t
        self.size = self.it.size
        print("Series includes the iterations :{}".format(self.it))
        data, data_info = self.ts.get_field(field=self.ts.avail_fields[0], coord="x", iteration=self.it[0])
        self.dims = numpy.shape(numpy.array(data))

    ## List all avaliable fields
    def listFields(self):
        print(self.ts.avail_fields)

    def electronEnergy(self, iteration: list[int], limits) -> None:
        plt.clf()
        plt.gcf()
        electronG = numpy.array(self.ts.get_particle(var_list = ["gamma"], iteration=iteration))
        electronW = numpy.array(self.ts.get_particle(var_list = ["w"], iteration=iteration))
        electronZ = numpy.array(self.ts.get_particle(var_list = ["z"], iteration=iteration))

        try:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            
        except ValueError:
            minz = -30.e-6
            maxz = 30.e-6
            maxG = 1
            maxW = 1
        else:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            maxG = electronG[0].max()
            maxW = electronW[0].max()

        ymax = numpy.ceil(limits[1])+1
        fig, ax = plt.subplots()
        data_array, xedges, yedges, quadmesh  = ax.hist2d(electronZ[0], electronG[0], weights = electronW[0],
                                                           bins=(self.dims[1],self.dims[0]), range = [[minz,maxz],[1,ymax]], norm = colors.LogNorm(vmin = 0.0001, vmax = maxW),
                                                           cmap="plasma" )

        self.hist_data = data_array
        self.yedges = yedges

        ax.ticklabel_format(axis = "x", style = "sci", scilimits = (-6,-6), useMathText = True)
        ax.set_xlabel("Z position (m)")
        ax.set_ylabel("Gamma ($\gamma$)")
        ax.set_ylim(bottom = limits[0], top = ymax)
        ax.set_facecolor((22/255, 6/255, 138/255))
        
        fig.colorbar(quadmesh, ax=ax)
        
        plt.axhline(y=maxG,color="r",linestyle="-")
        time = self.time_it[numpy.where(self.it == iteration[0])[0][0]]
        plt.title("Gamma in the mode {} at {}{} (iteration {})".format("all",numpy.round(time*10**15,1),"$e^{-15}$",iteration[0]))

    def electronEnergySpectrum(self, iteration: list[int], limits) -> None:
        plt.clf()
        plt.gcf()
        electronG = numpy.array(self.ts.get_particle(var_list = ["gamma"], iteration=iteration))
        electronW = numpy.array(self.ts.get_particle(var_list = ["w"], iteration=iteration))
        electronZ = numpy.array(self.ts.get_particle(var_list = ["z"], iteration=iteration))

        try:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            
        except ValueError:
            minz = -30.e-6
            maxz = 30.e-6
            maxG = 1
            maxW = 1
        else:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            maxG = electronG[0].max()
            maxW = electronW[0].max()

        ymax = numpy.ceil(limits[1])+1
        fig, ax = plt.subplots()
        data_array, xedges, yedges, quadmesh  = ax.hist2d(electronZ[0], electronG[0], weights = electronW[0],
                                                           bins=(self.dims[1],self.dims[0]), range = [[minz,maxz],[1,ymax]], norm = colors.LogNorm(vmin = 0.0001, vmax = maxW),
                                                           cmap="plasma" )

        plt.clf()
        plt.close()
        fig, ax = plt.subplots()
        ## Both Spectrum_data and yedges have a 1d Size of 600 

        spectrum_data = numpy.sum(data_array,axis = 0)
        spectrum_data = numpy.mean(spectrum_data.reshape(-1, 5), axis=1)

        new = yedges[:len(yedges)-1]                    
        yedges = numpy.mean(new.reshape(-1, 5), axis=1)

        plt.plot(yedges, spectrum_data)

        ##ax.ticklabel_format(axis = "x", style = "sci", scilimits = (-6,-6), useMathText = True)
        ax.set_ylabel("Density ($m^{-3}$)")
        ax.set_xlabel("Gamma ($\gamma$)")
        ax.set_facecolor((22/255, 6/255, 138/255))
        ax.set_yscale("log")
        
        time = self.time_it[numpy.where(self.it == iteration[0])[0][0]]
        plt.title("Gamma in the mode {} at {}{} (iteration {})".format("all",numpy.round(time*10**15,1),"$e^{-15}$",iteration[0]))

    def gammaRange(self):
        max = 1
        min = numpy.inf
        for iter in self.it:
            electronG = numpy.array(self.ts.get_particle(var_list = ["gamma"],iteration=iter))
            try:
                newMax = electronG[0].max()
                newMin = electronG[0].min()
            except ValueError:
                pass
            else:
                if newMax <= max:
                    pass
                else:    
                    max = newMax

                if newMin >= min:
                    pass
                else:
                    min = newMin

        if abs(min)< 1:
            y_error = abs(newMin)
            order = numpy.log10(y_error)
            order = numpy.floor(float(order))
            error = numpy.round(y_error*0.511,-int(order-1))
            bMax = numpy.round(max*0.511,-int(order-1))
        else:
            y_error = 0.01*max
            order = numpy.log10(y_error)
            order = numpy.floor(float(order))
            error = numpy.round(y_error*0.511,-int(order-1))
            bMax = numpy.round(max*0.511,-int(order-1))

        print(("Max Gamma is {} with a total energy of {}±{} MeV").format(max,bMax,error))
        if min == numpy.inf:
            min = 0
        return (min,max)

    def saveFigures(self, outDir: str="results",
                     iterations: list[int]= [],
                     fields_dict: dict={"B" : True, "E" : True, "J" : True, "rho" : True},
                     coords_dict: dict={"x" : True, "y" : True, "z" : True},
                     misc_dict  : dict={"graph_energy"      : False,"graph_3d_paticles" : False,"energy_spectrum"   : True, "gamma_heat" : True},
                     fps:int = 2) -> None:
        
        if not(os.path.isdir(self.cwd+"/"+outDir)):
            os.mkdir(self.cwd+"/"+outDir)
        
        ## Convert the dictionaries into a list
        fields = []
        for key in fields_dict:
            if fields_dict[key]:
                fields.append(key)

        coords = []
        for key in coords_dict:
            if coords_dict[key]:
                coords.append(key)

        ## Assign the lists to the ones avaliable
        if not iterations:
            iterations = self.it

        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        print("Starting write to file")
        for field_iter in fields:
            print("field  :{}".format(field_iter))
            if not (field_iter == "rho" or field_iter == "J" or field_iter == "E"):
                pass
            elif field_iter == "rho":
                coords = ["x"]
            elif field_iter == "E":
                coords = ["x","y","z"]
            else:
                coords = ["z"]
        
            for coord in coords:
                print("coord :{}".format(coord))
                max=0
                min=0 
                for iter in iterations: 
                    newMinMax = self.saveFigField(iter, field_iter, coord,retMax=True)
                    if newMinMax[1]>max:
                        max = newMinMax[1]

                    if newMinMax[0]<min:
                        min = newMinMax[0]

                fileList = [] 
                for iter in iterations: 
                    fileList.append(self.saveFigField(iter, field_iter, coord, norm=self.norm, limits=(min,max))) 

                if len(fileList) == 0:
                    print("No files to add")
                else:
                    self.itgLi(fileList,("{}_{}_gif.gif").format(field_iter,coord),fps) 
        
        if misc_dict["graph_energy"]:
            print("graph_energy")
            fileList=[]
            limits = self.gammaRange()
            for iter in iterations:
                self.electronEnergy([iter],limits)
                fileList.append(self.liSaveEnergy(iter))
            self.itgLi(fileList,("{}_energy_gif.gif").format(outDir),fps)

        if misc_dict["energy_spectrum"]:
            print("energy_spectrum")
            fileList=[]
            limits = self.gammaRange()
            for iter in iterations:
                self.electronEnergySpectrum([iter],limits)
                fileList.append(self.liSaveEnergySpectrum(iter))
            self.itgLi(fileList,("{}_energy_spectrum_gif.gif").format(outDir),fps)

        if misc_dict["graph_3d_paticles"]:
            print("graph_3d_paticles")
            pyvista.start_xvfb()
            plotter = pyvista.Plotter(off_screen = True)
            plotter.set_background([22/255, 6/255, 138/255])
            fileList = []
            limits = self.gammaRange()
            for iter in iterations:
                print("Iteration {}: 3D processing.".format(iter+1))
                fileList.append(self.view3D(outDir, iter, plotter, show = False))
                plotter.deep_clean()
                print("Iteration {}: 3D finished.".format(iter+1))
                
            print("3D gif creation started...")
            self.itgLi(fileList,("{}_3D.gif").format(outDir),fps)
            print("3D gif created sucessfully!")
            plotter.close()

        if misc_dict["gamma_heat"]:
            print("Gamma Heat")
            for iter in iterations: 
                max =0
                min = 0
                newMinMax = self.saveFigParticle(iter, "gamma",retMax=True)
                if newMinMax[1]>max:
                    max = newMinMax[1]

                if newMinMax[0]<min:
                    min = newMinMax[0]

            fileList=[]
            for iter in iterations:
                print(iter)
                if not(iter == 0):
                    fileList.append(self.saveFigParticle(iter, "gamma", norm=self.norm, limits=(min,max)))

                    
            self.itgLi(fileList,("{}_heat.gif").format(outDir),fps)
                      
        plt.close()

    def saveFigField(self, iter, field_iter, coord, retMax=False, limits = None, norm=None):
        plt.clf()
        plt.gcf()  
        if not (retMax) :
            if norm == "log":
                # Requires no negative nums, since data cannot be changed, cannot modify to fix
                self.ts.get_field(iteration=iter, field=field_iter, coord=coord, plot=True, norm=colors.LogNorm(vmin=1, vmax=limits[1]))
            elif norm == "symLog":
                self.ts.get_field(iteration=iter, field=field_iter, coord = coord, plot=True, norm=colors.SymLogNorm(linthresh=1, linscale=1, vmin=1, vmax=limits[1]))
            elif norm == "constant":
                self.ts.get_field(iteration=iter, field=field_iter, coord=coord, plot=True, vmin=limits[0], vmax=limits[1])
            else:
                self.ts.get_field(iteration=iter, field=field_iter, coord=coord, plot=True)
            
            return self.liSave(iter, field_iter, coord, dpi=300)
        else:
            data, data_info = self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=False)
            return data.min(), data.max()
        
    def saveFigParticle(self, iter, part_iter, retMax=False, limits = None, norm=None):
        plt.clf()
        plt.gcf()  
        
        if not (retMax) :
            data_x =  numpy.array(self.ts.get_particle(var_list = ["x"], iteration=iter, plot=False))

            minx = data_x[0].min()
            maxx = data_x[0].max()

            data_y =  numpy.array(self.ts.get_particle(var_list = ["y"], iteration=iter, plot=False))

            miny = data_y[0].min()
            maxy = data_y[0].max()

            data_z =  numpy.array(self.ts.get_particle(var_list = ["z"], iteration=iter, plot=False))

            minz = data_z[0].min()
            maxz = data_z[0].max()

            # print(data_x, data_y, len(data_x), len(data_y))
            if norm == "log":
                data = self.ts.get_particle(var_list = [part_iter], iteration=iter, plot=False, norm=colors.LogNorm(vmin=1, vmax=limits[1]))
                # Requires no negative nums, since data cannot be changed, cannot modify to fix
            elif norm == "symLog":
                data = self.ts.get_particle(var_list = [part_iter], iteration=iter, plot=False, norm=colors.SymLogNorm(linthresh=1, linscale=1, vmin=1, vmax=limits[1]))
            elif norm == "constant":
                data = self.ts.get_particle(var_list = [part_iter], iteration=iter, plot=False, vmin=limits[0], vmax=limits[1])
            else:
                data = self.ts.get_particle(var_list = [part_iter], iteration=iter, plot=False)
            
            fig, ax = plt.subplots()
            data_array_gamma, x_edges, z_edges, quadmesh_gamma  = ax.hist2d(data_z[0], data_x[0], weights = numpy.array(data)[0],
                                                          bins=(self.dims[1],self.dims[0]), range = [[minz, maxz],[-20.e-6,20.e-6]],
                                                           cmap="plasma" )

            data_array_number, x_edges, z_edges, quadmesh_number  = ax.hist2d(data_z[0], data_x[0],
                                                          bins=(self.dims[1],self.dims[0]), range = [[minz, maxz],[-20.e-6,20.e-6]],
                                                           cmap="plasma" )
            
            averaged_data = data_array_gamma / data_array_number
            ## averaged_quadmesh = quadmesh_gamma / quadmesh_number

            plt.clf()
            plt.gcf() 
            fig.set_size_inches(10,10)
            plt.imshow(averaged_data.transpose())

        
            ax.set_xlabel("Z position ($m$)")
            ax.set_ylabel("X Position ($m$)")
            ax.set_facecolor((22/255, 6/255, 138/255))

            ax.ticklabel_format(axis = "x", style = "sci", scilimits = (-6,-6), useMathText = True)
            ax.tick_params(axis="x", )

            ax.ticklabel_format(axis = "y", style = "sci", scilimits = (-6,-6), useMathText = True)
            fig.colorbar(cm.ScalarMappable(cmap="plasma"), ax=ax)

            plt.show()
            return self.liSave(iter, part_iter, "particle", dpi=300)
        else:
            data =  numpy.array(self.ts.get_particle(var_list = [part_iter], iteration=iter, plot=False))
            
            if data.size == 0:
                return 0, 50.e-6
            else:
                return data.min(), data.max()
            
    def itgLi(self, fileList: list[str], name: str = "default_field_B_timelapse.gif", fps: int = 1) -> None:
        # Create a gif folder in the result directory
        if not(os.path.exists("./{}/gifs".format(self.savePath))):
            os.mkdir("./{}/gifs".format(self.savePath))

        with imageio.get_writer("./{}/gifs/{}".format(self.savePath, name), mode='I', fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def liSave(self,iter: int,field_iter: str,coord: str,dpi: int=300) -> str:
        # Save figure in linux
        if not(os.path.exists("./{}/images".format(self.savePath))):
            os.mkdir("./{}/images".format(self.savePath))

        path = ("./{}/images/iter_{}_{}{}.png").format(self.savePath, iter.item(), field_iter, coord)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def liSaveEnergy(self, iter: int, dpi: int=300) -> str:
        # Save figure in linux
        if not(os.path.exists("./{}/images".format(self.savePath))):
            os.mkdir("./{}/images".format(self.savePath))

        path = ("./{}/images/iter_{}_Energy.png").format(self.savePath, iter.item())
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def liSaveEnergySpectrum(self, iter: int, dpi: int=300) -> str:
        # Save figure in linux
        path = ("./{}/images/iter_{}_Energy_spectrum.png").format(self.savePath, iter.item())
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path

    def view3D(self, outDir: str, iter: int, plotter: pyvista.plotter, show: bool = False, field: str = "rho"):
        # The theta=None argument constructs a 3D cartesian grid from the cylindrical data
        rho, meta = self.ts.get_field(field, iteration=iter, theta=None)
        grid = pyvista.ImageData()
        grid.dimensions = rho.shape
        grid.origin = [meta.xmin * 1e6, meta.ymin * 1e6, meta.zmin * 1e6]
        grid.spacing = [meta.dx * 1e6, meta.dy * 1e6, meta.dz * 1e6]
        grid.point_data['values'] = -rho.flatten(order='F')
        
        plotter.add_volume(grid, clim=(0, 4e6), opacity='geom', cmap='plasma', mapper='smart', show_scalar_bar=True)
        plotter.camera_position = "yz"
        plotter.camera.roll -= 90
        plotter.camera.azimuth = 45
        plotter.camera.elevation = 20
        plotter.show_axes()

        if show:
            plotter.show()
            
        if self.platform == "Linux" or self.platform == "linux":
            filename = "./{}/iter_{}_{}_3D_Render.ps".format(outDir, iter, field)
        elif self.platform == "Windows" or self.platform == "windows":
            filename = "{}\\{}\\iter_{}_{}_3D_Render.ps".format(self.cwd, outDir, iter, field)
        else:
            raise "Platform not supported"
        
        plotter.save_graphic(filename)
        
        return filename

    def side_slice(self, z_val: int):
        # help(self.ts.get_field)
        x, x_data = self.ts.get_field(field="rho", slice_across="z", slice_relative_position=z_val, plot=False, iteration=[100], plot_range=[[-15.e-6, 15.e-6], [None, None]])
        plt.show()

def main():
    
    fields = {"B" : False,
              "E" : False,
              "J" : False,
              "rho" : False}
    
    coords = {"x" : True,
              "y" : True}
    
    misc = {"graph_energy"      : False,
            "graph_3d_paticles" : False,
            "energy_spectrum"   : False,
            "gamma_heat" : True}

    outDir = sys.argv[1]
    print("Output directory is {}".format(outDir))

    print("Loading data files...")
    series = fbpic(norm=None, relativeInputPath = "/"+outDir+"/hdf5", savePath = outDir)
    print("Files loaded!")
    series.listFields()
    
    fps = series.size/7
    print("Gif FPS is {}".format(fps))

    print("Saving figures and creating gifs...")
    # PYVISTA DOES NOT WORK CURRENTLY!!!
    series.saveFigures(outDir=outDir, fields_dict=fields, coords_dict=coords, misc_dict = misc, fps=fps)
    print("Finished!")

if __name__ == "__main__":
    print("Running FBPIC_Image_Viking.py")
    print("Entering Main()...")
    main()
    print("Exiting Main()...")
    print("Finished!")