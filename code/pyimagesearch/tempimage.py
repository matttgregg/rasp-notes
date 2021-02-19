# import the necessary packages
import uuid
import os
import datetime

class TempImage:
  def __init__(self, name, basePath="./images/", ext=".jpg"):
    # construct the file path
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A_%d_%B_%Y_%I:%M:%S%p")
    self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
      rand=name + "_" + ts, ext=ext)
  def cleanup(self):
    # remove the file
    os.remove(self.path)
