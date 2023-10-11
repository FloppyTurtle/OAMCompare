import h5py, os, platform, subprocess
import imageio.v2 as imageio
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.cbook as cbook
import matplotlib.colors as colors
import numpy as np

class fbpic:
    def __init__(self, relativeInputPath = "/diags/hdf5",norm = None) -> None:
        ## Find what platform we are on necessary for saving files
        self.platform = platform.system()
        if not relativeInputPath:
            if self.platform == "Linux":
                relativeInputPath = "/diags/hdf5"
            elif self.platform == "Windows":
                relativeInputPath = "\\diags\\hdf5"

        ## Get the data input path and set it
        self.cwd = os.getcwd()
        self.inputDataPath =  self.cwd + relativeInputPath
        self.relativeInputPath = relativeInputPath
        self.norm = norm

        self.ts = OpenPMDTimeSeries(self.inputDataPath)
        self.it = self.ts.iterations
        self.time_it = self.ts.t
        self.size = self.it.size
        print("The following iterations are found in the data folder :{}".format(self.it))
        data, data_info = self.ts.get_field(field=self.ts.avail_fields[0],coord="x",iteration = self.it[0])
        self.dims = np.shape(np.array(data))

    ## List all avaliable fields
    def listFields(self):
        print(self.ts.avail_fields)

    ## This only seems to work in Juypter and not on my linux setup
    def slider(self):
        self.ts.slider()
        plt.show()

    def electronEnergy(self,iteration:list[int], limits) -> None:
        plt.clf()
        plt.gcf()
        electronG = np.array(self.ts.get_particle(var_list = ["gamma"], iteration=iteration))
        electronW = np.array(self.ts.get_particle(var_list = ["w"], iteration=iteration))
        electronZ = np.array(self.ts.get_particle(var_list = ["z"], iteration=iteration))
        try:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            maxG = electronG[0].max()
        except ValueError:
            minz = -30.e-6
            maxz = 30.e-6
        else:
            minz = electronZ[0].min()
            maxz = electronZ[0].max()
            maxG = 1

        fig, ax = plt.subplots()
        data_array, xedges, yedges, quadmesh  = ax.hist2d(electronZ[0], electronG[0], weights = electronW[0],
                                                           bins=(self.dims[1],self.dims[0]), range = [[minz,maxz],[1,limits[1]]] )
        #print("Edges are {} and {}".format(xedges,yedges))
        ax.ticklabel_format(axis = "x", style = "sci", scilimits = (-6,-6), useMathText = True)
        ax.set_xlabel("Z position (m)")
        ax.set_ylabel("Energy ($m_0c^2$)")
        ax.set_ylim(bottom = limits[0], top = limits[1])
        ax.set_facecolor((46/255,0,22/255))
        plt.axhline(y=maxG,color="r",linestyle="-")
        time = self.time_it[np.where(self.it == iteration[0])[0][0]]
        plt.title("Gamma in the mode {} at {}{} (iteration {})".format("all",np.round(time*10**15,1),"$e^{-15}$",iteration[0]))

    def gammaRange(self):
        max = 1
        for iter in self.it:
            electronG = np.array(self.ts.get_particle(var_list = ["gamma"],iteration=iter))
            try:
                newMax = electronG[0].max()
            except ValueError:
                pass
            else:
                if newMax < max:
                    pass
                else:    
                    max = newMax

        return (1,max)

    def saveFigures(self, outDir: str="results",
                     iterations: list[int]= [],
                     fields: list[str]=[],
                     particles:list[str]=[],
                     coords: list[str] = ["x"],
                     energy: bool = False, 
                     fps:int = 2) -> None:
        
        ## Create the result directory
        if self.platform == "Linux" or self.platform == "linux":
            if not(os.path.isdir(self.cwd+"/"+outDir)):
                subprocess.run(["mkdir", outDir])
        else:
            if not(os.path.isdir(self.cwd+"\\"+outDir)):
                os.mkdir(self.cwd+"\\"+outDir)
                               

        ## Assign the lists to the ones avaliable
        if not iterations:
            iterations = self.it

        if not energy:
            if not fields:
                fields = self.ts.avail_fields


        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        print("Starting write to file")
        if self.platform == "Linux" or self.platform == "linux":
            for field_iter in fields:
                print("field  :{}".format(field_iter))
                if field_iter == "rho" or field_iter == "J":
                    for coord in ["x"]:
                        print("coord :{}".format(coord))
                        max=0
                        min=0 
                        for iter in iterations: 
                            newMinMax = self.saveFig(iter, field_iter, coord, outDir,retMax=True)
                            if newMinMax[1]>max:
                                max = newMinMax[1]

                            if newMinMax[0]<min:
                                min = newMinMax[0]

                        print(min,max)
                        fileList = []
                        for iter in iterations: 
                            fileList.append(self.saveFig(iter, field_iter, coord, outDir,norm=self.norm, limits=(min,max))) 
                        self.itgLi(fileList,outDir,("{}_{}:gif.gif").format(field_iter,coord),fps) 
                else:
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

                        self.itgLi(fileList,outDir,("{}_{}:gif.gif").format(field_iter,coord),fps) 
            
            fileList=[]
            limits = self.gammaRange()
            for iter in iterations:
                self.electronEnergy([iter],limits)
                fileList.append(self.liSaveEnergy(outDir, iter))
            self.itgLi(fileList, outDir,("{}_energy_gif.gif").format(outDir),fps)

        elif self.platform == "Windows" or self.platform == "windows":
            for field_iter in fields:
                print("field  :{}".format(field_iter))
                if field_iter == "rho" or field_iter == "J":
                    for coord in ["x"]:
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
                            fileList.append(self.saveFig(iter, field_iter, coord, outDir,norm=self.norm, limits=(min,max))) 

                        self.itgWin(fileList,outDir,("{}_{}-gif.gif").format(field_iter,coord),fps) 
                else:
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

                        print(min,max)
                        fileList = []
                        for iter in iterations: 
                            fileList.append(self.saveFig(iter, field_iter, coord, outDir, norm=self.norm, limits=(min,max))) 
                        
                        self.itgWin(fileList,outDir,("{}_{}-gif.gif").format(field_iter,coord),fps) 
            
            fileList = []
            limits = self.gammaRange()
            for iter in iterations:
                self.electronEnergy([iter],limits)
                fileList.append(self.winSaveEnergy(outDir, iter))
            self.itgWin(fileList, outDir,("{}_energy_gif.gif").format(outDir),fps)

    def saveFig(self,iter,field_iter,coord,outDir,retMax=False,limits = None, norm=None):
        plt.clf()
        plt.gcf()  
        if not(retMax) :  
            if norm == "log":
                ## Requires no negative nums, since data cannot be changed, cannot modify to fix
                self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=True, norm = colors.LogNorm(vmin=1, vmax = limits[1]))
            elif norm == "symLog":
                self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=True, norm = colors.SymLogNorm(linthresh=1,linscale=1,vmin=1, vmax = limits[1]))
            else:
                self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=True)
            
            if self.platform == "Linux" or self.platform == "linux":
                return self.liSave(outDir,iter,field_iter,coord,dpi=300)
            else:
                return self.winSave(outDir,iter,field_iter,coord,dpi=300)
        else:
            data, data_info = self.ts.get_field(iteration=iter, field = field_iter, coord = coord, plot=False)
            return (data.min(),data.max())
            
    def itgLi(self,fileList: list[str],outDir: str,name: str="efault_field_B_timelapt.gif",fps: int = 1) -> None:
        ## Create a gif folder in the result directory
        if not(os.path.exists(("./{}/gifs").format(outDir))):
            os.mkdir("./{}/gifs".format(outDir))

        with imageio.get_writer(("./{}/gifs/{}").format(outDir,name),mode='I',fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def itgWin(self,fileList: list[str],outDir: str,name: str="efault_field_B_timelapt.gif",fps: int = 1) -> None:
        ## Creating a gif folder in the results directory
        if not(os.path.exists(("{}\\{}\\gifs").format(self.cwd,outDir))):
            os.mkdir(("{}\\{}\\gifs").format(self.cwd,outDir))
        
        with imageio.get_writer(("{}\\{}\\gifs\\{}").format(self.cwd,outDir,name),mode='I',fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)

    def liSave(self,outDir: str,iter: int,field_iter: str,coord: str,dpi: int=300) -> str:
        ## Save figure in linux
        path = ("./{}/iter:{}:{}{}.png").format(outDir,iter.item(),field_iter,coord)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def liSaveEnergy(self,outDir: str,iter: int, dpi: int=300) -> str:
        ## Save figure in linux
        path = ("./{}/iter:{}:Energy.png").format(outDir,iter.item())
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path

    def winSave(self,outDir: str,iter:int ,field_iter: str,coord: str,dpi=300):
        ## Save figure in windows
        path = "{}\\{}\\iter-{}-{}{}.png".format(self.cwd,outDir,iter,field_iter,coord)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path
    
    def winSaveEnergy(self,outDir: str,iter:int, dpi=300):
        ## Save figure in windows
        path = "{}\\{}\\iter-{}-Energy.png".format(self.cwd,outDir,iter)
        plt.savefig(path, dpi=dpi)
        plt.close()
        return path

series = fbpic(norm = None)
series.listFields()
outDir = str(input("Enter a output directory for this run  :"))
##outDir = "Test 2"
fps = series.size/5
print("Gif FPS is {}".format(fps))
##series.saveFigures(outDir=outDir,coords=["x","y"],fps=fps)
series.saveFigures(outDir=outDir,fields=[],coords=["x"],fps=fps,energy=True)
##series.electronEnergy(iteration=[950])

