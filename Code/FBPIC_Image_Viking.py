import os, sys, numpy, pyvista, platform
import imageio.v2 as imageio
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib.pyplot as plt
import matplotlib.colors as colors

class fbpic:
    def __init__(self, relativeInputPath="/diags/hdf5", norm=None) -> None:
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
        #print("Edges are {} and {}".format(xedges,yedges))
        ax.ticklabel_format(axis = "x", style = "sci", scilimits = (-6,-6), useMathText = True)
        ax.set_xlabel("Z position (m)")
        ax.set_ylabel("Gamma ($\gamma$)")
        ax.set_ylim(bottom = limits[0], top = ymax)
        ax.set_facecolor((22/255, 6/255, 138/255))
        
        fig.colorbar(quadmesh, ax=ax)
        
        plt.axhline(y=maxG,color="r",linestyle="-")
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
        print(("Max Gamma is {} with a total energy of {}±{} GeV").format(max,bMax,error))
        if min == numpy.inf:
            min = 0
        return (min,max)

    def saveFigures(self, outDir: str="results",
                     iterations: list[int]= [],
                     fields: list[str]=[],
                     particles:list[str]=[],
                     coords: list[str] = ["x"],
                     just_energy: bool = False, 
                     skip_energy: bool = False,
                     just_3d: bool = False, 
                     skip_3d: bool = False,
                     fps:int = 2) -> None:
        
        ## Create the result directory
        if self.platform == "Linux" or self.platform == "linux":
            if not(os.path.isdir(self.cwd+"/"+outDir)):
                os.mkdir(self.cwd+"/"+outDir)
        else:
            if not(os.path.isdir(self.cwd+"\\"+outDir)):
                os.mkdir(self.cwd+"\\"+outDir)
                               

        ## Assign the lists to the ones avaliable
        if not iterations:
            iterations = self.it

        if not (just_energy or just_3d):
            if not fields:
                fields = self.ts.avail_fields


        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        print("Starting write to file")
        if self.platform == "Linux" or self.platform == "linux":
            for field_iter in fields:
                print("field  :{}".format(field_iter))
                if not (field_iter == "rho" or field_iter == "J"):
                    pass
                elif field_iter == "rho":
                    coords = ["x"]
                else:
                    coords = ["z"]
            
                for coord in coords:
                    print("coord :{}".format(coord))
                    max=0
                    min=0 
                    for iter in iterations: 
                        newMinMax = self.saveFig(iter, field_iter, coord, outDir,retMax=True)
                        if newMinMax[1]>max:
                            max = newMinMax[1]

                        if newMinMax[0]<min:
                            min = newMinMax[0]

                    fileList = [] 
                    for iter in iterations: 
                        fileList.append(self.saveFig(iter, field_iter, coord, outDir, norm=self.norm, limits=(min,max))) 

                    self.itgLi(fileList,outDir,("{}_{}_gif.gif").format(field_iter,coord),fps) 
            
            ## Make energy graph
            if not(skip_energy):
                fileList=[]
                limits = self.gammaRange()
                for iter in iterations:
                    self.electronEnergy([iter],limits)
                    fileList.append(self.liSaveEnergy(outDir, iter))
                self.itgLi(fileList, outDir,("{}_energy_gif.gif").format(outDir),fps)

            if not(skip_3d):
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
                self.itgLi(fileList, outDir,("{}_3D.gif").format(outDir),fps)
                print("3D gif created sucessfully!")
                plotter.close()
                
        elif self.platform == "Windows" or self.platform == "windows":
            for field_iter in fields:
                print("field :{}".format(field_iter))
                if not (field_iter == "rho" or field_iter == "J"):
                    pass
                elif field_iter == "rho":
                    coords = ["x"]
                else:
                    coords = ["z"]
                    
                for coord in coords:
                    print("coord :{}".format(coord))
                    max=0
                    min=0 
                    for iter in iterations: 
                        newMinMax = self.saveFig(iter, field_iter, coord, outDir,retMax=True)
                        if newMinMax[1]>max:
                            max = newMinMax[1]

                        if newMinMax[0]<min:
                            min = newMinMax[0]

                    print(min, max)
                    fileList = []
                    for iter in iterations: 
                        fileList.append(self.saveFig(iter, field_iter, coord, outDir, norm=self.norm, limits=(min,max))) 
                    
                    self.itgWin(fileList, outDir, ("{}_{}-gif.gif").format(field_iter,coord),fps)
        
            
            if not(skip_energy):
                fileList = []
                limits = self.gammaRange()
                for iter in iterations:
                    self.electronEnergy([iter],limits)
                    fileList.append(self.winSaveEnergy(outDir, iter))
                self.itgWin(fileList, outDir,("{}_energy_gif.gif").format(outDir),fps)
             
            if not(skip_3d):
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
                self.itgWin(fileList, outDir,("{}_3D.gif").format(outDir),fps)
                print("3D gif created sucessfully!")
                plotter.close()
                 
        plt.close()

    def saveFig(self, iter, field_iter, coord, outDir, retMax=False, limits = None, norm=None):
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
            
            if self.platform == "Linux" or self.platform == "linux":
                return self.liSave(outDir, iter, field_iter, coord, dpi=300)
            else:
                return self.winSave(outDir, iter, field_iter, coord, dpi=300)
        else:
            data, data_info = self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=False)
            return data.min(), data.max()
            
    def itgLi(self,fileList: list[str],outDir: str, name: str = "default_field_B_timelapse.gif", fps: int = 1) -> None:
        # Create a gif folder in the result directory
        if not(os.path.exists("./{}/gifs".format(outDir))):
            os.mkdir("./{}/gifs".format(outDir))

        with imageio.get_writer("./{}/gifs/{}".format(outDir, name), mode='I', fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def itgWin(self,fileList: list[str],outDir: str,name: str="default_field_B_timelapt.gif",fps: int = 1) -> None:
        # Creating a gif folder in the results directory
        if not(os.path.exists("{}\\{}\\gifs".format(self.cwd, outDir))):
            os.mkdir("{}\\{}\\gifs".format(self.cwd, outDir))
        
        with imageio.get_writer("{}\\{}\\gifs\\{}".format(self.cwd, outDir, name), mode='I', fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def liSave(self,outDir: str,iter: int,field_iter: str,coord: str,dpi: int=300) -> str:
        # Save figure in linux
        path = ("./{}/iter_{}_{}{}.png").format(outDir, iter.item(), field_iter, coord)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def liSaveEnergy(self, outDir: str, iter: int, dpi: int=300) -> str:
        # Save figure in linux
        path = ("./{}/iter:{}:Energy.png").format(outDir, iter.item())
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path

    def winSave(self, outDir: str, iter:int , field_iter: str, coord: str, dpi=300):
        # Save figure in windows
        path = "{}\\{}\\iter-{}-{}{}.png".format(self.cwd,outDir,iter,field_iter,coord)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def winSaveEnergy(self, outDir: str, iter: int, dpi=300):
        # Save figure in windows
        path = "{}\\{}\\iter-{}-Energy.png".format(self.cwd, outDir, iter)
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
    outDir = sys.argv[1]
    ##outDir = "500_2000_Laguerre_Gaussian"
    print("Output directory is {}".format(outDir))

    print("Loading data files...")
    series = fbpic(norm=None, relativeInputPath = "/"+outDir+"/data")
    print("Files loaded!")
    series.listFields()

    fps = series.size/7
    print("Gif FPS is {}".format(fps))

    print("Saving figures and creating gifs...")
    # PYVISTA DOES NOT WORK CURRENTLY!!!
    series.saveFigures(outDir=outDir, fields=[], particles=[], coords=["x","y"], fps=fps, just_energy=False, skip_energy=False, just_3d=False, skip_3d=True)
    print("Finished!")


if __name__ == "__main__":
    print("Running FBPIC_Image_Viking.py")
    print("Entering Main()...")
    main()
    print("Exiting Main()...")
    print("Finished!")