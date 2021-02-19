# import the necessary packages
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
#import dropbox
import imutils
import json
import time
import cv2
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
  help="path to the JSON configuration file")

args = vars(ap.parse_args())

# filter warnings, load the configuration and initialize the Dropbox client
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None
lastFrame = None
# check to see if the Dropbox should be used
if conf["use_dropbox"]:
  # connect to dropbox and start the session authorization process
  #client = dropbox.Dropbox(conf["dropbox_access_token"])
  print("[SUCCESS] dropbox account (IGNORED)")

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  timestamp = datetime.datetime.now()
  ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
  #print("[TICK] {}".format(ts))
  # grab the raw NumPy array representing the image and initialize
  # the timestamp and occupied/unoccupied text
  frame = f.array
  text = ""
  # resize the frame, convert it to grayscale, and blur it
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  # if the average frame is None, initialize it
  if avg is None:
    print("[INFO] starting background model...")
    avg = gray.copy().astype("float")
    rawCapture.truncate(0)
    t = TempImage("Boot")
    cv2.imwrite(t.path, frame)
    lastFrame = frame
    continue

  # accumulate the weighted average between the current frame and
  # previous frames, then compute the difference between the current
  # frame and running average
  cv2.accumulateWeighted(gray, avg, 0.5)
  frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
  # threshold the delta image, dilate the thresholded image to fill
  # in holes, then find contours on thresholded image
  thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
    cv2.THRESH_BINARY)[1]
  thresh = cv2.dilate(thresh, None, iterations=2)
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)

  if (timestamp - lastUploaded).seconds >= conf["heartbeat_seconds"]:
    text = "Heartbeat" 

  bbox = ''
  # loop over the contours
  for c in cnts:
    # if the contour is too small, ignore it
    if cv2.contourArea(c) < conf["min_area"]:
      continue
    # compute the bounding box for the contour, draw it on the frame,
    # and update the text
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if text == '':
      text = "Passing"
    if y + h > 100:
      text = "Drive"
    bbox = '{}({},{},{},{})'.format(bbox, x, y, x + w, y + h) 

  # check to see if the room is occupied
  if text != "":
    # draw the text and timestamp on the frame
    cv2.putText(frame, "{}".format(text), (10, 20),
      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
      0.35, (0, 0, 255), 1)

    # check to see if enough time has passed between uploads
    if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
      # increment the motion counter
      motionCounter += 1
      # check to see if the number of frames with consistent motion is
      # high enough
      if motionCounter >= conf["min_motion_frames"]:
        # check to see if dropbox sohuld be used
        if conf["use_dropbox"]:
          # write the image to temporary file
          t = TempImage(text)
          cv2.imwrite(t.path, frame)
          # upload the image to Dropbox and cleanup the tempory image
          print("[UPLOAD] {}".format(ts))
          path = "/{base_path}/{timestamp}.jpg".format(
              base_path=conf["dropbox_base_path"], timestamp=ts)
          client.files_upload(open(t.path, "rb").read(), path)
          t.cleanup()
        else:
          # write the image to temporary file
          t = TempImage(text)
	  lt = TempImage(text + "-1")
          cv2.imwrite(t.path, frame)
          cv2.imwrite(lt.path, lastFrame)
          # upload the image to Dropbox and cleanup the tempory image
          print("[SAVE] {}".format(ts))

        # update the last uploaded timestamp and reset the motion
        # counter
        lastUploaded = timestamp
        motionCounter = 2
  # otherwise, the room is not occupied
  else:
    motionCounter = 0

  lastFrame = frame

  # check to see if the frames should be displayed to screen
  if conf["show_video"]:
    # display the security feed
    cv2.imshow("Security Feed", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
      break

  # clear the stream in preparation for the next frame
  rawCapture.truncate(0)
