import os, time, calendar, subprocess
import sdf_helper as sh
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import transforms,image
import imageio.v2 as imageio

class graphCreation:
    def __init__(self,fileName="0001.sdf",filePath="epoch-4.17.15/epoch2d/Data/",outputDir="default_deck_images", dataList = []):
        ## filePath is the path to the sdf pile directory
        ## outputDir is the directory that the images will be output to
        ## fileName is self edvident

        self.currentPath = os.getcwd()
        self.data = sh.getdata(filePath + fileName)
        self.outDir = outputDir
        self.fileName = fileName
        self.filePath = filePath
        if dataList == "":
            self.dataList = ["dist_fn_x_px_electron",
                "Magnetic_Field_Bx", "Magnetic_Field_By", "Magnetic_Field_Bz",
                "Electric_Field_Ex", "Electric_Field_Ey", "Electric_Field_Ez",
                "Derived_Charge_Density", "Derived_Number_Density", "Derived_Number_Density_electron",
                "Derived_Average_Particle_Energy", "Derived_Average_Particle_Energy_electron",
                "Current_Jx", "Current_Jy", "Current_Jz"]
        else:
            self.dataList = dataList

    def displayData(self,filename):
        ## lists all the variables stored in the stf file
        sh.list_variables(self.data)

    def save2DFigSingle(self, varName,yBound=(-20,20),colourMap = "afmhot"):
        ## saves the sdf data graphs to the directory defined in the __init__ statement

        if not(os.path.exists(os.getcwd()+"/"+self.outDir+"/"+self.fileName)):
            os.mkdir(self.outDir+"/"+self.fileName)
            ## creates the directory if the directory doesn't exist
        
        savename = self.outDir + "/"+self.fileName+"/" + self.fileName + varName
        return_arr = []
        if varName == "dist_fn_x_px_electron" or varName == "dist_fn_y_py_electron":
            dims = getattr(getattr(self.data, varName),"dims")
            localData = getattr(getattr(self.data, varName), "data")
            npData = np.array(localData)

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(1/(1+np.exp(-npData)), interpolation='nearest', aspect="auto",cmap=colourMap)
            plt.colorbar()
            plt.savefig(savename + "_sigmoid.png", dpi = 300)
            return_arr.append(savename + "_sigmoid.png")

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(np.log(npData + 1), interpolation='nearest', aspect="auto", cmap=colourMap)
            plt.colorbar()
            plt.savefig(savename + "_log.png", dpi=300)
            return_arr.append(savename + "_log.png")

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(npData, interpolation='nearest', aspect="auto", cmap=colourMap)
            plt.colorbar()
            plt.savefig(savename+ ".png", dpi=300)
            return_arr.append(savename+ ".png")

            print("File saved.")
        else:
            if not((savename + ".png") in (os.listdir(self.outDir + "/"+self.fileName+"/"))):
                try:
                    x = getattr(self.data, varName)
                    sh.clf()
                    plt.pcolormesh(x.grid_mid.data[0], x.grid_mid.data[1], x.data.T, shading="auto", cmap="plasma")
                    plt.savefig(savename + ".png")
                    print("File saved successfully")
                except TypeError:
                    print("Type Error")
                else:
                    return_arr.append(savename+ ".png")
            else:
                subprocess.run(["cd", self.outDir, "|", "rm", self.fileName + varName + ".png"])
                try:
                    x = getattr(self.data, varName)
                    fig = plt.pcolormesh(x.grid_mid.data[0], x.grid_mid.data[1], x.data.T, shading="auto", cmap="plasma")
                    plt.savefig(savename + ".png")
                    print("File saved successfully")
                except TypeError:
                    print("Type Error") ## there is always almost a class error for the first data set
                else:
                    return_arr.append(savename+ ".png")
        plt.close()

        return return_arr

    def save2DFigAll(self, colourMap = "afmhot"):
        ## saves the sdf data graphs to the directory defined in the __init__ statement
        if not(os.path.exists(os.getcwd()+"/"+self.outDir+"/"+self.fileName)):
            os.mkdir(self.outDir+"/"+self.fileName)
            ## creates the directory if the directory doesn't exist

        test = graphCreation(self.fileName, self.filePath, self.outDir)
        outputFiles = []
        for i in range(len(self.dataList)):
            file_paths = test.save2DFigSingle(self.dataList[i])
            for file in file_paths:
                outputFiles.append(file)

        plt.close()
        self.outputFiles = outputFiles

    def imgToGif(self,Fps = 5):
        ## converts the output directory of sdf files to gifs of all data types.
        

        if not(os.path.exists("./{}/gifs".format(self.savePath))):
            os.mkdir("./{}/gifs".format(self.savePath))

        with imageio.get_writer("./{}/gifs/{}".format(self.savePath, name), mode='I', fps=fps) as writer:
            for nameOfFile in fileList:
                image = imageio.imread(nameOfFile)
                writer.append_data(image)


        if (fileName[8:] + "_time_lapse.gif") in os.listdir(self.outDir):
            subprocess.run(["rm", self.outDir + "/" + fileName[8:] + "_time_lapse.gif"])
            print("File already exists, deleting the previous")

        with imageio.get_writer(self.outDir + "/" + fileName[8:] + "_time_lapse.gif", mode='I',fps=Fps) as writer:
            for nameOfFile in sortedImgDict:
                image = imageio.imread(self.outDir + "/" + nameOfFile[:8] + "/" + nameOfFile)
                writer.append_data(image)



        print("GIFs saved")

    def save2DFolder(self):
        dirList = os.listdir(self.filePath)
        sdfList=[]
        for i in range(len(dirList)):
            if ".sdf" in dirList[i]:
                sdfList.append(dirList[i])
        sdfSorted = sorted(sdfList)
        for fileNames in sdfSorted:
            test = graphCreation(fileName=fileNames, filePath=self.filePath,
                                 outputDir=self.outDir)
            print(fileNames)
            test.save2DFigAll()

    def watchSim(self):
        ##Used process data as it comes out of Epoch, will wait for 30 hours or until there are

        test = graphCreation(fileName=self.fileName,
                             filePath=self.filePath,
                             outputDir=self.outDir)

        pastList = os.listdir(self.outDir)
        print(len(pastList),(len(pastList) < (fileLimit+17)))

        dirList = os.listdir(self.filePath)
        sdfList = []
        for i in range(len(dirList)):
            if ".sdf" in dirList[i]:
                sdfList.append(dirList[i])

        newPastList = []
        for i in range(len(pastList)):
            if ".sdf" in pastList[i]:
                newPastList.append(pastList[i])

        newSdfList=sorted(sdfList)
        for i in range(len(newPastList)):
            newSdfList.remove(newPastList[i])

        for filename in newSdfList:
            print("Start of image creation, file name :"+filename)
            test = graphCreation(fileName=filename,
                                    filePath=self.filePath,
                                    outputDir=self.outDir)
            test.save2DFigAll()
            print("processed")

        if len(newSdfList) == 0:
            test = graphCreation(fileName=self.fileName,
                                    filePath=self.filePath,
                                    outputDir=self.outDir)

        pastList=sdfList

        test.imgToGif()

    def saveMultFolders(self,filePathList=[], outDirList=[]):
        if len(filePathList) == 0  or len(outDirList) == 0:
            filePathList.append(self.filePath)
            outDirList.append(self.outDir)

        if len(filePathList) == len(outDirList):
            for i in range(len(filePathList)):
                if not (os.path.exists(os.getcwd() + "/" + outDirList[i])):
                    os.mkdir(outDirList[i])
                    ## creates output folder

                test = graphCreation(fileName="0000.sdf",
                                     filePath=filePathList[i],
                                     outputDir=outDirList[i])
                test.save2DFolder()
                test.imgToGif()
        else:
            print("Lists must have the same dimensions as they map 1 to 1 input to output.")


dataList = ["Magnetic_Field_Bx", "Magnetic_Field_By", "Magnetic_Field_Bz",
                "Electric_Field_Ex", "Electric_Field_Ey", "Electric_Field_Ez",
                "Derived_Charge_Density", "Derived_Number_Density", "Derived_Number_Density",
                "Derived_Average_Particle_Energy", "Derived_Average_Particle_Energy_electron",
                "Current_Jx", "Current_Jy", "Current_Jz"]

test = graphCreation(fileName="0000.sdf",
                     filePath="User_Epoch/LWFA/",
                     outputDir="User_Epoch/LWFA_Output", dataList=dataList )
 
print(test.dataList)
test.watchSim(fileLimit=100)
##used to make data as its produced from epoch
#test.save2DFolder()
## used to save a folders worth of sdf files
#test.save2DfigSingle("dist_fn_x_px_electron")
# USed to save a single type of graph for the chosen SDF file
print("Finished")


#test.save2DfigSingle("dist_fn_x_px_electron")



