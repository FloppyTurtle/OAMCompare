import sdf
import os
import sdf_helper as sh
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import transforms,image
import subprocess
import imageio
import time
import calendar

class graphCreation:
    dataList = ["dist_fn_x_px_electron",
                "Magnetic_Field_Bx", "Magnetic_Field_By", "Magnetic_Field_Bz",
                "Electric_Field_Ex", "Electric_Field_Ey", "Electric_Field_Ez",
                "Derived_Charge_Density", "Derived_Number_Density", "Derived_Number_Density_electron",
                "Derived_Average_Particle_Energy", "Derived_Average_Particle_Energy_electron",
                "Current_Jx", "Current_Jy", "Current_Jz"]

    def __init__(self,fileName="0001.sdf",filePath="epoch-4.17.15/epoch2d/Data/",outputDir="default_deck_images"):
        ## filePath is the path to the sdf pile directory
        ## outputDir is the directory that the images will be output to
        ## fileName is self edvident

        self.currentPath = os.getcwd()
        self.data = sh.getdata(filePath + fileName)
        self.outDir = outputDir
        self.fileName = fileName
        self.filePath = filePath

    def displayData(self,filename):
        ## lists all the variables stored in the stf file

        sh.list_variables(self.data)

    def save2DFigSingle(self, varName,yBound=(-20,20),colourMap = "afmhot"):
        ## saves the sdf data graphs to the directory defined in the __init__ statement

        if not(os.path.exists(os.getcwd()+"/"+self.outDir+"/"+self.fileName)):
            subprocess.run(["mkdir", self.outDir+"/"+self.fileName])
            ## creates the directory if the directory doesn't exist

        if varName == "dist_fn_x_px_electron" or varName == "dist_fn_y_py_electron":
            dims = getattr(getattr(self.data, varName),"dims")
            localData = getattr(getattr(self.data, varName), "data")
            npData = np.array(localData)

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(1/(1+np.exp(-npData)), interpolation='nearest', aspect="auto",cmap=colourMap)
            plt.colorbar()
            plt.savefig(self.outDir + "/"+self.fileName+"/" + self.fileName + varName + "_sigmoid.png", dpi = 300)

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(np.log(npData + 1), interpolation='nearest', aspect="auto", cmap=colourMap)
            plt.colorbar()
            plt.savefig(self.outDir + "/" + self.fileName + "/" + self.fileName + varName + "_log.png", dpi=300)

            plt.clf()
            plt.gcf()
            plt.figure(figsize=(10, 10))
            fig = plt.imshow(npData, interpolation='nearest', aspect="auto", cmap=colourMap)
            plt.colorbar()
            plt.savefig(self.outDir + "/" + self.fileName + "/" + self.fileName + varName + ".png", dpi=300)

            print("File saved.")
        else:
            if not((self.outDir + "/"+self.fileName+"/" + self.fileName + varName + ".png") in (os.listdir(self.outDir + "/"+self.fileName+"/"))):
                try:
                    x = getattr(self.data, varName)
                    sh.clf()
                    plt.pcolormesh(x.grid_mid.data[0], x.grid_mid.data[1], x.data.T, shading="auto", cmap="plasma")
                    plt.savefig(self.outDir + "/"+self.fileName+"/" + self.fileName + varName + ".png")
                    print("File saved successfully")
                except TypeError:
                    print("Type Error")
            else:
                subprocess.run(["cd", self.outDir, "|", "rm", self.fileName + varName + ".png"])
                try:
                    x = getattr(self.data, varName)
                    fig = plt.pcolormesh(x.grid_mid.data[0], x.grid_mid.data[1], x.data.T, shading="auto", cmap="plasma")
                    plt.savefig(self.outDir + "/" + self.fileName+"/" +self.fileName+ varName + ".png")
                    print("File saved successfully")
                except TypeError:
                    print("Type Error") ## there is always almost a class error for the first data set
        plt.close()

    def save2DFigAll(self, colourMap = "afmhot"):
        ## saves the sdf data graphs to the directory defined in the __init__ statement
        if not(os.path.exists(os.getcwd()+"/"+self.outDir+"/"+self.fileName)):
            subprocess.run(["mkdir", self.outDir+"/"+self.fileName])
            ## creates the directory if the directory doesn't exist

        test = graphCreation(self.fileName, self.filePath, self.outDir)
        for i in range(len(self.dataList)):
            ##
            test.save2DFigSingle(self.dataList[i])

        plt.close()

    def imgToGif(self,Fps = 5):
        ## converts the output directory of sdf files to gifs of all data types.

        print("imgToGif")
        x = os.listdir(self.outDir)
        print(x)
        folderList = []
        for i in range(len(x)):
            if str(x[i][len(x[i])-3:]) == "sdf":
                folderList.append(x[i])
        fileList = os.listdir(self.outDir+"/"+str(folderList[0]))
        #print(fileList, folderList)
        adjustFileList = []
        for i in range(len(fileList)):
            adjustFileList.append(fileList[i][8:])


        for fileName in adjustFileList:
            nameList = []
            imgdict = {"zzzz" : "hello"}
            for folderName in folderList:
                listdir = os.listdir(self.outDir+"/"+folderName)
                if len(adjustFileList) != len(listdir):
                    test = graphCreation(fileName=folderName,filePath=self.filePath,outputDir=self.outDir)
                    test.save2DFigAll()

                found = False
                i = 0
                while not found:
                    if fileName == listdir[i][8:]:
                        found = True
                        targetFile = listdir[i]
                    else:
                        i += 1


                imgdict[targetFile] = self.outDir+"/"+folderName+"/"+targetFile

            sortedImgDict = sorted(imgdict)
            sortedImgDict.remove("zzzz")
            imgList = []
            for i in range(len(sortedImgDict)):
                imgList.append(imgdict.get(sortedImgDict[i]))

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

    def watchSim(self,fileLimit = 50, timeLimit = 108000):
        ##Used process data as it comes out of Epoch, will wait for 30 hours or until there are

        test = graphCreation(fileName=self.fileName,
                             filePath=self.filePath,
                             outputDir=self.outDir)

        pastList = os.listdir(self.outDir)
        print(len(pastList),(len(pastList) < (fileLimit+17)))
        x = calendar.timegm(time.gmtime())
        while (calendar.timegm(time.gmtime()) - x <timeLimit) and (len(pastList) < (fileLimit+17)):
            print(calendar.timegm(time.gmtime()) - x)
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

            test.imgToGif()
            pastList=sdfList
            print("Wait start.")
            time.sleep(300)
            print("Wait end.")

        test.imgToGif()

    def saveMultFolders(self,filePathList=[], outDirList=[]):
        if len(filePathList) == 0  or len(outDirList) == 0:
            filePathList.append(self.filePath)
            outDirList.append(self.outDir)

        if len(filePathList) == len(outDirList):
            for i in range(len(filePathList)):
                if not (os.path.exists(os.getcwd() + "/" + outDirList[i])):
                    subprocess.run(["mkdir", outDirList[i]])
                    ## creates output folder

                test = graphCreation(fileName="0000.sdf",
                                     filePath=filePathList[i],
                                     outputDir=outDirList[i])
                test.save2DFolder()
                test.imgToGif()
        else:
            print("Lists must have the same dimensions as they map 1 to 1 input to output.")

    def dev(self):
        ## Class testing definition

        print(os.listdir(os.getcwd()+"/"+self.outDir))


test = graphCreation(fileName="0000.sdf",
                     filePath="epoch-4.17.15/epoch2d/Data_2/",
                     outputDir="10_laser_decks/92fs_mk3")
test.watchSim(fileLimit=100)
##used to make data as its produced from epoch
#test.save2DFolder()
## used to save a folders worth of sdf files
#test.save2DfigSingle("dist_fn_x_px_electron")
# USed to save a single type of graph for the chosen SDF file
print("Finished")


#test.save2DfigSingle("dist_fn_x_px_electron")



