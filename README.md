# rasp-notes
Notes on configuring and setting up Raspberry PI

# Basic SetUp

Go here, follow the instructions: https://www.raspberrypi.org/documentation/installation/installing-images/

For a basic installation, the no desktop Raspberry Pi OS Lite works well.

Once done, hook up a keyboard, monitor and power and get started.

* Default login is User:pi Password:raspberry
* Find the SSID for the netword. Best way is: `sudo iwlist wlan0 scan`
* Use `raspi-config` to set up the wireless with this SSID.

Create a new user:
 * Create a user: `sudo adduser bob` with an appropriate password.
 * Give the user the right permissions: `sudo adduser bob sudo`
   * Other useful groups are i2c, camera.
 * Add more users if you like!
 * Delete any users that you don't want! (`sudo userdel -r badbob` The `-r` arg deletes the associated home directory.)

Usability enhancements:
  * Change the network name of the Pi to something useful, memorable.
  * Enable SSH in `raspi-config`
  * Configure your passwordless login (`ssh-copy-id <USERNAME>@<IP-ADDRESS>` from the remote to the Pi).
  * Update package repository: `apt-get update`

Systemd:

Set up some local servies using `systemd` 

* See documentation for writing a service, or see local scripts.
* Copy the unit scripts to `/etc/systemd/system/`
* `systemctl` is now your friend for your services.
* Commands include:
  * `start/stop/restart` for running the service directly.
  * `enable/disable` for enabling the service to start automatically.
  * Possinly need `daemon-reload` after editing unit files. And likely `reenable` for the edited service. 
  * More details: https://www.commandlinux.com/man-page/man1/systemctl.1.html

Camera Usage:

GPIO Usage:
