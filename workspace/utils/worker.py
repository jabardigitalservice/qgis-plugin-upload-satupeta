import json
import os
import requests

from zipfile import ZipFile
from PyQt5.QtCore import QThread, pyqtSignal

from ..utils.config import readSetting


class WorkerThread(QThread):

    worker_complete = pyqtSignal(dict)
    progress = pyqtSignal(float)

    def __init__(self, source,tipeFile):
        super(QThread, self).__init__()
        #print('workerinit')
        self.stopworker = False # initialize the stop variable

        self.source = source
        self.tipeFile = tipeFile

    def run(self):


        #init progress 
        self.progress.emit(0)

        shp = self.source.replace(self.tipeFile, ".shp")
        shp = shp.replace("\\", "/")
        prj = self.source.replace(self.tipeFile, ".prj")
        prj = prj.replace("\\", "/")
        dbf = self.source.replace(self.tipeFile, ".dbf")
        dbf = dbf.replace("\\", "/")
        shx = self.source.replace(self.tipeFile, ".shx")
        shx = shx.replace("\\", "/")

        self.progress.emit(1)

        #for check if necessary
        #sourceFile = json.loads('{"shp":"%s","prj":"%s","dbf":"%s","shx":"%s"}'%(shp,prj,dbf,shx))

        zipShp = ZipFile(f"{shp.split('.')[0]}"+'.zip', 'w')
        # Add multiple files to the zip
        zipShp.write(f"{shp}",os.path.basename(shp).replace(" ","_"))
        zipShp.write(f"{dbf}",os.path.basename(dbf).replace(" ","_"))
        zipShp.write(f"{shx}",os.path.basename(shx).replace(" ","_"))
        zipShp.write(f"{prj}",os.path.basename(prj).replace(" ","_"))
        # close the Zip File
        zipShp.close()

        self.progress.emit(2)

        #path zip
        files_path = shp.split('.')[0]+'.zip'

        #read store setting
        self.username = readSetting("username")
        self.password = readSetting("password")
        self.opdcode = readSetting("opdcode")

        headers = {
            'user': self.username,
            'password': self.password,
            'opdcode': self.opdcode
        }

        #another endpoint upload_v2 or upload/
        url = 'http://geoplugin.coredatajds.id/gis/plugin/upload_v2'

        if files_path:

            #name file
            file_name = shp.split('.')[0].split('/')[-1]
            file_extension = ".zip"

            self.progress.emit(3)

            #sent file
            response = requests.post(url, headers=headers,files=[
                ('file',(file_name+file_extension,
                open(files_path,'rb'),
                'application/zip'))
            ],verify=False)

            self.progress.emit(4)

            if response:
                if response.status_code == 200:
                    self.worker_complete.emit({"status":response.status_code,"message":"OK"})
                else:
                    self.progress.emit(0)
                    err_msg = response.json().get('detail').get('message')
                    self.worker_complete.emit({"status":response.status_code,"message":err_msg})
            else:
                self.progress.emit(0)
                self.worker_complete.emit({"status":417,"message":"Failed Upload"})
        else:
            self.progress.emit(0)
            self.worker_complete.emit({"status":416,"message":"Empty File"})

        #delete file tmp
        os.remove(files_path)
