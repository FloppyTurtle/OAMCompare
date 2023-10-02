class fbpic:
    import h5py, os
    from openpmd_viewer import OpenPMDTimeSeries
    import matplotlib.pyplot as plt
    import openpmd_api as io

    
    
    def __init__(self, relativeInputPath = "\\diags\\hdf5"):
        self.cwd = os.getcwd()
        self.inputDataPath =  self.cwd + relativeInputPath
        self.relativeInputPath = relativeInputPath

        self.ts = OpenPMDTimeSeries(inputDataPath)
        self.it = self.ts.iterations
        print(it)

    def listFields(self):
        self.ts.avail_fields

        

for iter in it: 
    rho, info_rho = ts.get_field( iteration=iter, field='rho',plot=True )
    plt.show()
    plt.close()