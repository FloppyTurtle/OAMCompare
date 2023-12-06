import os, sys, subprocess
import numpy as np
import sdf_helper as sh
from matplotlib import pyplot as plt
from matplotlib import transforms,image
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import matplotlib.colors as colors


class EPOCH_im:
    def __init__(self, relativeInputPath="/diags/hdf5", savePath = "", norm=None) -> None:
        # Find what platform we are on necessary for saving files
        print("fbpic data object created.")
        if relativeInputPath == "/diags/hdf5":
            print("Default file path used, changing based on platform (Linux/Windows).")
            relativeInputPath = "/diags/hdf5"
            print("Platform is Linux hence path is {}".format(relativeInputPath))


        # Get the data input path and set it
        self.cwd = os.getcwd()
        self.savePath = savePath
        self.inputDataPath = self.cwd + relativeInputPath
        self.norm = norm

        temp_dir = os.listdir(self.inputDataPath)
        sdf_files = []
        for file in temp_dir:
            if "sdf" in file:
                sdf_files.append(file)

        self.sdf_files = sdf_files

        if len(sdf_files) == 0:
            raise FileNotFoundError("No SDF files found!")

        self.size = len(sdf_files)

        print("SDF series files found...")


    ## List all avaliable fields
    def listFields(self):
        zeroth_data = sh.getdata("{}/0001.sdf".format(self.inputDataPath))
        sh.list_variables(zeroth_data)

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

    def saveFigures(self, outDir: str="results", files: [int] = [], attributes_dict: dict = {}, fps:int = 2) -> None:
        
        if not(os.path.isdir(self.cwd+"/"+outDir)):
            os.mkdir(self.cwd+"/"+outDir)
        
        ## Assign the lists to the ones avaliable
        if not files:
            files = self.sdf_files

        attributes = []
        for key in attributes_dict:
            if attributes_dict[key]:
                attributes.append(key)

        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        print("Starting write to file")
        sortedFiles = sorted(files)
        for attr in attributes: 
           
            fileList = [] 
            for file in sortedFiles:
                fileData = sh.getdata("{}/{}".format(self.inputDataPath,file))
                fileList.append(self.saveFig(fileData, attr, file, norm=self.norm)) 

            if len(fileList) == 0:
                print("No files to add")
            else:
                print("Creating Gif...")
                self.itgLi(fileList,("{}_gif.gif").format(attr),fps) 
                print("Gif finished!")
            
                         
        plt.close()

    def saveFig(self, data, attr, file, norm=None):
        plt.clf() 
        sh.clf()
        plt.figure(figsize=(10, 10))
        grid = data.Grid_Grid
        x = getattr(data, attr)
        #help(x)
        plt.pcolormesh(grid.data[0], grid.data[1], x.data.T[1], shading = "auto", cmap="plasma")

        return self.liSave(attr, file, norm, dpi=300)
               
    def itgLi(self, fileList: [str], name: str = "", fps: int = 1) -> None:
        # Create a gif folder in the result directory
        if not(os.path.exists("./{}/gifs".format(self.savePath))):
            os.mkdir("./{}/gifs".format(self.savePath))

        with imageio.get_writer("./{}/gifs/{}".format(self.savePath, name), mode='I', fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def liSave(self, attr: str, file: str, norm, dpi: int=300) -> str:
        # Save figure in linux
        if not(os.path.exists("./{}".format(self.savePath))):
            os.mkdir("./{}".format(self.savePath))

        if not(os.path.exists("./{}/images".format(self.savePath))):
            os.mkdir("./{}/images".format(self.savePath))

        if norm == None:
            path = ("./{}/images/iter_{}_{}.png").format(self.savePath, file, attr)
        else:
            path = ("./{}/images/iter_{}_{}_{}.png").format(self.savePath, file, attr, norm)
        
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

    def side_slice(self, z_val: int):
        # help(self.ts.get_field)
        x, x_data = self.ts.get_field(field="rho", slice_across="z", slice_relative_position=z_val, plot=False, iteration=[100], plot_range=[[-15.e-6, 15.e-6], [None, None]])
        plt.show()

    def dev(self, outDir):
        data = sh.getdata("{}/0015.sdf".format(self.inputDataPath))
        sh.list_variables(data)
        ey = data.Electric_Field_Modes_Exm_real
        grid = data.Grid_Grid
        print(dir(grid))
        print(grid.dims)
        x = ey.data
        print(ey.data.T)

        plt.pcolormesh(grid.data[0], grid.data[1], ey.data.T[1], shading = "auto")
        plt.show()

        plt.savefig("test.png")
        plt.close()


def main():
    
    attributes = {"Electric_Field_Modes_Erm_imag" : True,
                    "Electric_Field_Modes_Erm_real" : True,
                    "Electric_Field_Modes_Etm_imag" : True,
                    "Electric_Field_Modes_Etm_real" : True,
                    "Electric_Field_Modes_Exm_imag" : True,
                    "Electric_Field_Modes_Exm_real" : True,
                    "Magnetic_Field_Modes_Brm_imag" : True,
                    "Magnetic_Field_Modes_Brm_real" : True,
                    "Magnetic_Field_Modes_Btm_imag" : True,
                    "Magnetic_Field_Modes_Btm_real" : True,
                    "Magnetic_Field_Modes_Bxm_imag" : True,
                    "Magnetic_Field_Modes_Bxm_real" : True}

    outDirup = sys.argv[1]
    print("Output directory is {}".format(outDirup))

    print("Loading data files...")
    series = EPOCH_im(norm=None, relativeInputPath = "/"+outDirup, savePath = "test_sdf")
    print("Files loaded!")
    ##series.listFields()
    
    fps = series.size/7
    print("Gif FPS is {}".format(fps))

    print("Saving figures and creating gifs...")
    ##series.dev(outDirup)
    series.saveFigures(outDir=outDirup, attributes_dict=attributes, fps=fps)
    print("Finished!")

if __name__ == "__main__":
    print("Running FBPIC_Image_Viking.py")
    print("Entering Main()...")
    main()
    print("Exiting Main()...")
    print("Finished!")