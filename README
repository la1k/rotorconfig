Overview
========

Configuration files and scripts for enabling simple setup of networked rotor
control from Linux, for multiple rotors, and for enabling support for rotor
control from specific Windows applications (i.e. N1MM).

A description can be found at https://www.la1k.no/2017/09/15/unified-software-rotor-control-over-the-local-network/.

Setup
=====

1. Review and test serial port configuration in 70-la1k-symlinks.rules.

For a serial port device at /dev/ttyUSB0, run `udevadm info -p -a /dev/ttyUSB0`
to find information that can uniquely identify the serial device. See the
.rules-file for examples for one specific usb-device containing 4 serial ports.
Here, each serial port is enumerated from 0 to 3, and uniquely defined by these
port numbers, and symlinks like /dev/tty_HFROT are set up to point to e.g.
/dev/ttyUSB0.

Note that the device must be plugged in and out for changes in udev
configuration to take place. New udev rules placed in /etc/udev/rules.d/ are
loaded automatically by udev.

2. Review rotor configuration in rotors.conf.

Example configuration for a rotor:

[40m_80m-array]
n1mm_freqbands=7.0 3.5
rotctld_port=4555
rotctld_options=""
rotctld_model=902
device=/dev/tty_HFROT

In this case, commands sent from n1mm will be forwarded to this rotor on 7.0
and 3.5 MHz bands, and rotctld will be started on port 4555. Assumed device
file is /dev/tty_HFROT, and the model is 902 (rot1prog).  Extra rotctld options
could be specified in rotctld_options without quotation marks.

n1mm_freqbands is optional, if ommitted, no commands will be forwarded to this rotor
from n1mm.

Name of the rotor should probably not contain whitespaces or any special
characters like '/'.

3. Run ./installation.sh to copy scripts, configuration files and service files
to the correct locations (or do this manually based on the contents of the script).

Each rotor is started as a separate systemd service, called rotctld@{rotorname}.service.
In the above example, the service would be called rotctld@40m_80m-array.service.
The n1mm receiver is started as n1mm-rotctl.service.

Check whether there were any errors using `systemctl status rotctld@*`.
Convenience script `check_rotors.sh` can also be used to print rotor angles
from all the rotors using rotctl.

File/folder overview
====================

installation.sh: Installation script. Installs service files to systemd
folders, rotor configuration to /usr/local/etc/ and executables to
/usr/local/bin and reloads systemd. Rerun this if configuration in rotors.conf
is changed.

rotors.conf: Defines setup for each rotor. The field `n1mm_freqbands` defines
for which frequency bands rotor commands from N1MM should be forwarded this
rotor.

70-la1k-symlinks.rules: udev rules for serial ports, giving them nice names.

n1mm-rotctld/: Contains script for receiving rotor commands from n1mm and
forwarding them to the correct rotctld instance (defined in rotors.conf), and
corresponding systemd service file.

rotctld-service-files/: Contains script for starting rotctld based on
configuration in rotors.conf, and corresponding systemd service file.
