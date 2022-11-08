from qgis.core import (
    QgsMessageLog,
    QgsSettings,
    Qgis,
)
settings = QgsSettings()

def logMessage(message, level=Qgis.Info):
    """
    Logger untuk debugging
    """
    QgsMessageLog.logMessage(message, "Plugin-QGIS-JDS", level=level)

def readSetting(key, default=None):
    """
    Read value from QGIS Settings
    """
    logMessage("Mengambil data " + str(key) + " dari memory proyek QGIS")
    try:
        return settings.value("plugin_qgis_jds/" + str(key), default)
    except Exception:
        logMessage("gagal memuat data")
    settings.sync()

def storeSetting(key, value):
    """
    Store value to QGIS Settings
    """
    settings.setValue("plugin_qgis_jds/" + str(key), value)
    logMessage("Menyimpan data " + str(key) + " pada memory proyek QGIS")
    settings.sync()