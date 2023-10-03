import h5py, os, platform, subprocess
import imageio.v2 as imageio
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class fbpic:
    def __init__(self, relativeInputPath = "") -> None:
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

        self.ts = OpenPMDTimeSeries(self.inputDataPath)
        self.it = self.ts.iterations
        print(self.it)

    ## List all avaliable fields
    def listFields(self):
        print(self.ts.avail_fields)

    ## This only seems to work in Juypter and not on my linux setup
    def slider(self):
        self.ts.slider()
        plt.show()

    def saveFigures(self, outDir: str="results",
                     iterations: list[int]= [],
                     fields: list[str]=[],
                     particles:list[str]=[],
                     coord: str = "x") -> None:
        
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

        if not fields:
            fields = self.ts.avail_fields

        if not particles:
            particles = self.ts.avail_species


        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        print("Starting write to file")
        if self.platform == "Linux" or self.platform == "linux":
            for field_iter in fields:
                fileList = []
                print(("Field {} saved.").format(field_iter))
                for iter in iterations: 
                    plt.clf()
                    plt.gcf()
                    self.ts.get_field(iteration=iter, field = field_iter, coord = "x",plot=True)
                    fileList.append(self.liSave(outDir,iter,field_iter,coord,dpi=300))
                
                self.itgLi(fileList,outDir,("{}_{}:gif.gif").format(field_iter,coord),fps= 2) 

        
        elif self.platform == "Windows" or self.platform == "windows":
            for field_iter in fields:
                fileList = []
                print(("Field {} saved.").format(field_iter))
                for iter in iterations: 
                    plt.clf()
                    plt.gcf()
                    self.ts.get_field(iteration=iter, field = field_iter, coord = "x", plot=True)
                    fileList.append(self.winSave(outDir,iter,field_iter,coord,dpi=300))
                
                self.itgWin(fileList,outDir,("{}_{}-gif.gif").format(field_iter,coord),fps= 2) 
                    

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

    ## Linux save function using the correct file notation
    def liSave(self,outDir: str,iter: int,field_iter: str,coord: str,dpi: int=300) -> str:
        ## Save figure in linux
        path = ("./{}/iter:{}:{}{}.png").format(outDir,iter.item(),field_iter,coord)
        plt.savefig(path, dpi=dpi)
        return path
    
    ## Windows save notation using the correct notation
    def winSave(self,outDir: str,iter:int ,field_iter: str,coord: str,dpi=300):
        ## Save figure in windows
        path = "{}\\{}\\iter-{}-{}{}.png".format(self.cwd,outDir,iter,field_iter,coord)
        plt.savefig(path, dpi=dpi)
        return path

series = fbpic()
series.listFields()
series.saveFigures()


""" for iter in it: 
    rho, info_rho = ts.get_field( iteration=iter, field='rho',plot=True )
    plt.show()
    plt.close() """