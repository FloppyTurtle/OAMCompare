import h5py, os, platform
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib.pyplot as plt
import openpmd_api as io
import subprocess

class fbpic:
    def __init__(self, relativeInputPath = ""):
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

    def saveFigures(self, outDir:"CWD/outdir"="results",
                     iterations:"SPecific iteratations" = [],
                     fields:"Specific fields"=[],
                     particles:"Specific particles"=[]):
        
        ## Create the result directory
        if not(os.path.exists(self.cwd+"/"+outDir)):
            subprocess.run(["mkdir", outDir])

        ## Assign the lists to the ones avaliable
        if not iterations:
            iterations = self.it

        if not fields:
            fields = self.ts.avail_fields

        if not particles:
            particles = self.ts.avail_species


        ## Same function but one for linux and one for windows since the address
        ## method is different for each operating system
        if self.platform == "Linux" or self.platform == "linux":
            for field_iter in fields:
                fileList = []
                for iter in iterations: 
                    plt.clf()
                    plt.gcf()
                    var, var_info = self.ts.get_field(iteration=iter,field =  field_iter,slice_across=["z"])
                    plt.colorbar()
                    fileList.append(self.liSave(outDir,iter,field_iter,dpi=300))

        elif self.platform == "Windows" or self.platform == "windows":
            for field_iter in fields:
                fileList = []
                for iter in iterations: 
                    plt.clf()
                    plt.gcf()
                    var, var_info = self.ts.get_field(iteration=iter,field =  field_iter,slice_across=["z"])
                    plt.colorbar()
                    fileList.append(self.liSave(outDir,iter,field_iter,dpi=300))

                    

    def itg(self,fps = 1):
        pass

    ## Linux save function using the correct file notation
    def liSave(self,outDir,iter,field_iter,dpi):
        path = "./"+outDir+"/iter:"+iter+":"+field_iter+".png"
        plt.savefig(path, dpi=300)
        return path
    
    ## Windows save notation using the correct notation
    def winSave(self,outDir,iter,field_iter,dpi):
        path = self.cwd+"\\"+outDir+"\\iter:"+iter+":"+field_iter+".png"
        plt.savefig(path, dpi=300)
        return path

series = fbpic()
series.listFields()
#series.slider()

""" for iter in it: 
    rho, info_rho = ts.get_field( iteration=iter, field='rho',plot=True )
    plt.show()
    plt.close() """