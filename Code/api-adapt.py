import h5py, os, platform
from openpmd_viewer import OpenPMDTimeSeries
import matplotlib.pyplot as plt
import openpmd_api as io
import subprocess

class fbpic:
    def __init__(self, relativeInputPath = ""):
        if relativeInputPath == "":
            if platform.system() == "Linux":
                relativeInputPath = "/diags/hdf5"
            elif platform.system() == "Windows":
                relativeInputPath = "\\diags\\hdf5"


        self.cwd = os.getcwd()
        self.inputDataPath =  self.cwd + relativeInputPath
        self.relativeInputPath = relativeInputPath

        self.ts = OpenPMDTimeSeries(self.inputDataPath)
        self.it = self.ts.iterations
        print(self.it)

    def listFields(self):
        print(self.ts.avail_fields)

    def slider(self):
        self.ts.slider()
        plt.show()

    def saveFigures(self,outDir="results",iterations = [],fields=[],particles=[]):
        if not(os.path.exists(self.cwd+"/"+outDir)):
            subprocess.run(["mkdir", outDir])

        for iter in self.it:
            for field_iter in fields:
                plt.clf()
                plt.gcf()
                var, var_info = self.ts.get_field(iteration=iter,field =  field_iter,slice_across=["z"])


series = fbpic()
series.listFields()
#series.slider()

""" for iter in it: 
    rho, info_rho = ts.get_field( iteration=iter, field='rho',plot=True )
    plt.show()
    plt.close() """