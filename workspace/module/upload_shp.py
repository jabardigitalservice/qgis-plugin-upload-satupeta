# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UploadSHPDialog
                                 A QGIS plugin
 example
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-10-27
        git sha              : $Format:%H$
        copyright            : (C) 2022 by misdan
        email                : jds.dataengineer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import requests
import json
import pandas as pd
import numpy as np
from zipfile import ZipFile

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from PyQt5.QtCore import pyqtSignal
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer

from ..utils.config import readSetting
from ..utils.table_model import TableModel

#notif
from ..module.notif_sukses import NotifSukses
from ..module.notif_gagal import NotifGagal

#loading screen
from ..module.loading_screen import LoadingScreen

#worker
from ..utils.worker import WorkerThread

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/upload.ui'))


class UploadSHPDialog(QtWidgets.QDialog, FORM_CLASS):

    UserLogout = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(UploadSHPDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        #list dialog
        self.notifOK = NotifSukses()
        self.notifGagal = NotifGagal()
        self.LoadingScreen = LoadingScreen()

        #list button
        self.pbUploadSHP.clicked.connect(self.onpbUploadSHPClicked)
        self.pbLogOut.clicked.connect(self.onpbLogOutClicked)
        self.pbMulaiUlang.clicked.connect(self.onpbMulaiUlangClicked)
        self.select_layer.currentTextChanged.connect(self.onSelectLayerClicked)
        self.reloadpushButton.clicked.connect(self.tabChanged)
        self.clearpushButtonID.clicked.connect(self.clearStyle)
        self.ButtonClearNameLayer.clicked.connect(self.clearNameLayer)

        
        #list emmit
        self.notifOK.notifikasiSukses.connect(self.ok_sukses_button)
        self.notifGagal.notifikasiGagal.connect(self.ok_gagal_button)

        #listener tab widget
        self.tabWidget_main_menu.currentChanged.connect(self.reload)


    def tabChanged(self):
        if (self.tabWidget_main_menu.currentIndex() == 1):
            self.list_file_queue()
            #print("asafdf")
        # elif(self.tabWidget_main_menu.currentIndex() == 2):
        #     self.restart_file()
        #     print('asdf')
    
    def reload(self):
        self.list_file_queue()
    

    def clearStyle(self):
        self.lineEdit_id_antrian.setText('')


    def clearNameLayer(self):
        self.nama_layer.setText('')
        self.progresBarUploadMain.setValue(0)


    def onpbUploadSHPClicked(self):

        #show loading
        #self.LoadingScreen.show()

        layerName = self.select_layer.currentText()

        layer = QgsProject().instance().mapLayersByName(layerName)[0]
        source = layer.source()
  
        source = source.split("|")
        tipe = source[0].split(".")[-1]
        
        nama_layer = self.nama_layer.text()

        #SLD File
        source_sld = source[0]
        sldPath = source_sld.replace(".shp", ".sld")
        sldPath = sldPath.replace("\\", "/")
        layer.saveSldStyle(sldPath)

        #SRID Save to .txt
        source_srid = source[0]
        sridPath = source_srid.replace(".shp", ".txt")
        # layer = QgsVectorLayer(sridPath, 'Shapefile', 'ogr')
        crs = layer.crs()
        with open(sridPath, 'w') as file:
            file.write(str(crs))
        

        #throw to worker
        if (tipe=="shp"):
            self.worker = WorkerThread(source[0],".shp",nama_layer)
            self.worker.start()
            self.worker.worker_complete.connect(self.onFinishedThreadUpload)
            #self.worker.progress.connect(self.onProgressBar)
            self.worker.progress.connect(self.onProgressBarMain)
        elif (tipe=="dbf"):
            self.worker = WorkerThread(source[0],".dbf",nama_layer)
            self.worker.start()
            self.worker.worker_complete.connect(self.onFinishedThreadUpload)
            #self.worker.progress.connect(self.onProgressBar)
            self.worker.progress.connect(self.onProgressBarMain)
        elif (tipe=="shx"):
            self.worker = WorkerThread(source[0],".shx",nama_layer)
            self.worker.start()
            self.worker.worker_complete.connect(self.onFinishedThreadUpload)
            #self.worker.progress.connect(self.onProgressBar)
            self.worker.progress.connect(self.onProgressBarMain)
        elif (tipe=="prj"):
            self.worker = WorkerThread(source[0],".prj",nama_layer)
            self.worker.start()
            self.worker.worker_complete.connect(self.onFinishedThreadUpload)
            #self.worker.progress.connect(self.onProgressBar)
            self.worker.progress.connect(self.onProgressBarMain)


    def onFinishedThreadUpload(self, emp):
        
        #hide loading screen
        self.LoadingScreen.hide()

        if (emp["status"] == 200):
            #show notif
            msg = 'Unggah Berhasil!'
            self.notifOK.show()
            self.notifOK.lbl_notif_sukses.setText(msg)
        elif (emp["status"] == 416):
            #show notif
            err_msg = "Berkas tidak boleh kosong"
            self.notifGagal.show()
            self.notifGagal.lbl_notif_gagal.setText(err_msg)
        elif (emp["status"] == 417):
            #show notif
            err_msg = "Gagal, Harap ulangi kembali"
            self.notifGagal.show()
            self.notifGagal.lbl_notif_gagal.setText(err_msg)
        else:
            #show notif
            err_msg = emp["message"]
            self.notifGagal.show()
            self.notifGagal.lbl_notif_gagal.setText(err_msg)
    

    def onProgressBar(self, val):
        self.LoadingScreen.progressBarUpload.setValue((val/4)*100)
    

    def onProgressBarMain(self, val):
        self.progresBarUploadMain.setValue((val/4)*100)

    
    # table view
    def list_file_queue(self):
        #read store setting
        self.username = readSetting("username")
        self.password = readSetting("password")
        self.opdcode = readSetting("opdcode")
        
        headers = {
            'user': self.username,
            'password': self.password,
            'opdcode': self.opdcode
        }

        url = 'https://api.coredatajds.id/gis/list_queue_file'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            #get data
            data = response.json()
            df = pd.DataFrame (data, columns = ['id','object_name','status','created_at','last_modified','link_wms','link_download','information'])
            
            #cleansing
            df['status'] = df['status'].str.replace("_"," ")
            df['status'] = df['status'].str.upper().str.title()

            df['created_at'] = df['created_at'].astype('datetime64[ns]')
            df['created_at'] = df['created_at'].dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta')
            df['created_at'] = df['created_at'].dt.strftime('%d/%m/%y %H:%M')

            df['last_modified'] = df['last_modified'].astype('datetime64[ns]')
            df['last_modified'] = df['last_modified'].dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta')
            df['last_modified'] = df['last_modified'].dt.strftime('%d/%m/%y %H:%M')

            df = df.replace(np.nan, '', regex=True)

            df.columns = ['id', 'nama_file', 'status', 'dibuat_pada','terakhir_diubah','link_wms','link_download','information']
            
            df.columns = df.columns.str.replace('_',' ')
            df.columns = df.columns.str.upper()
            df.index = np.arange(1, len(df) + 1)

            self.model = TableModel(df)
            self.tblview_list_file.setModel(self.model)

            #modified style table
            self.tblview_list_file.setWordWrap(True)
            self.tblview_list_file.resizeRowsToContents()
            # self.tblview_list_file.resizeColumnsToContents()
    
    # def restart_file(self):
    #     self.pbMulaiUlang.clicked.connect(self.onpbMulaiUlangClicked)


    def onpbMulaiUlangClicked(self):
        id_queue = self.lineEdit_id_antrian.text()
        print(id_queue)
        #name_file = self.lineEdit_id_antrian.text()
         
        if id_queue:
            #read store setting
            self.username = readSetting("username")
            self.password = readSetting("password")
            self.opdcode = readSetting("opdcode")
            
            #bucket_name = "temp2"

            headers = {
                'user': self.username,
                'password': self.password,
                'opdcode': self.opdcode
            }

            url = 'https://api.coredatajds.id/gis/plugin/admin/restart_queue_file'
            #url = 'https://api.coredatajds.id/gis/plugin/admin/insert_queue_file'

            payload = json.dumps({
                "id_queue": id_queue,
            })
            
            #payload = json.dumps({
            #    "bucket_name": bucket_name,
            #    "file_name":name_file
            #})

            response = requests.post(url, headers=headers, data=payload)

            if response.status_code == 200:
                msg = 'Mulai Ulang Antrian Berhasil!'
                self.notifOK.show()
                self.notifOK.lbl_notif_sukses.setText(msg)
            else:
                err_msg = response.json().get('detail').get('message')
                self.notifGagal.show()
                self.notifGagal.lbl_notif_gagal.setText(err_msg)
        else:
            self.notifGagal.show()
            self.notifGagal.lbl_notif_gagal.setText('ID Antrian tidak boleh kosong')

    # Handle
    def onSelectLayerClicked(self):
        self.select_layer.currentText()
    

    def onpbLogOutClicked(self):
        self.UserLogout.emit()    


    def ok_sukses_button(self):
        #self.choosefileSHP.closeEvent()
        self.notifOK.hide()


    def ok_gagal_button(self):
        #self.choosefileSHP.closeEvent()
        self.notifGagal.hide()