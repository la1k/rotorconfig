#!/usr/bin/env python

# Receives rotor commands from N1MM (logging program used in Windows) and
# forwards these to the approriate rotctld instance based on the frequency band
# in the messages. Details on the assumed N1MM protocol is found at
# http://n1mm.hamdocs.com/tiki-index.php?page=Rotator+Control#Rotator_UDP_Packet_Information
# (2017-08-12).
#
# Correspondence between frequency band and rotctld connection
# is defined in an external configuration file. See documentation
# for class rotor_mapper below for details.
#
# Based on perl prototype written by LA6YKA Norvald H. Ryeng
# (https://home.samfundet.no/~ryeng/n1mm-rotctl)
#
# Converted to python and extended by LA3WUA Oyvind Karlsen and LA9SSA Asgeir
# Bjorgan.

import re
import socket
import sys
import ConfigParser

# Provides connections to multiple rotctld instances and rotor selection based
# on frequency band. Commands can be sent to these using send_azimuth_command()
# and send_stop_command(), where rotors are selected based on the input
# frequency band. This can be used for rotor selection when handling rotor
# commands sent from N1MM (which will include a frequency band).
#
# Mapping between frequency band and rotctld instance is provided by a separate
# file (see constructor of this class). Example format:
#
# [rotor 1]
# n1mm_freqbands=14.0 7.0
# rotctld_port=5677
# ...
#
# [rotor 2]
# n1mm_freqbands=50.0
# rotctld_port=4763
# ...
#
# Here, the rotctld instance at localhost:5677 will be selected when N1MM
# wants to turn a rotor at the 14.0 MHz or 7.0 MHz frequency bands.
class rotor_mapper:
    ## Rotctld connections
    rotctld_connections = {}
    ## Mapping between N1MM frequency bands and index in rotctld connection array
    freq_to_connection_mapper = {}

    # Connect to rotctld instances and construct mapping between frequency
    # bands sent by N1MM and the corresponding connections.
    #
    # \param config_filename Filename for config file with mapping between
    #        rotctld server info and corresponding frequency bands
    def __init__(self, config_filename):
        #load config file
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_filename, "r"))
        connection_number = 0;
        for rotor in config.sections():
            FREQBAND_OPTION = "n1mm_freqbands"
            if config.has_option(rotor, FREQBAND_OPTION):
                bands_str = config.get(rotor, FREQBAND_OPTION)
                bands = bands_str.split()

                port = int(config.get(rotor, "rotctld_port"))

                #connect to rotctld on specified host and port
                try:
                    rotctl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    rotctl.connect(('', port))
                    self.rotctld_connections[connection_number] = rotctl

                    #add frequency bands to lookup table
                    for band in bands:
                        self.freq_to_connection_mapper[band] = connection_number

                    connection_number += 1
                except Exception, e:
                    print("Failed to connect to rotctld on localhost:" + str(port) + " (frequency bands: " + bands_str + "): " + str(e))
                    exit(1)


    # Get rotctld socket corresponding to the input frequency band.
    #
    # \param frequency_band Frequency band
    # \return Rotctld socket
    def get_rotctld_connection(self, frequency_band):
        try:
            rotctl = self.rotctld_connections[self.freq_to_connection_mapper[frequency_band]]
            return rotctl
        except:
            return None

    # Send azimuth command to rotctld instance corresponding to input frequency
    # band.
    #
    # \param frequency_band Frequency band
    # \param azimuth Azimuth in degrees
    def send_azimuth_command(self, frequency_band, azimuth):
        rotctl = self.get_rotctld_connection(frequency_band)
        if rotctl: rotctl.send("P " + azimuth + " 0.0\n")

    # Send stop command to rotctld instance corresponding to input frequency
    # band.
    #
    # \param frequency_band Frequency band
    def send_stop_command(self, frequency_band):
        rotctl = self.get_rotctld_connection(frequency_band)
        if rotctl: rotctl.send("S\n")

if (len(sys.argv) < 2):
    print "Usage: " + sys.argv[0] + " [config_file]"
    exit(1)

#set up rotors and frequency band correspondence
rotors = rotor_mapper(sys.argv[1])

#n1mm receiver
n1mm = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
n1mm.bind(('', 12040))

#patterns for matching against incoming rotor control XML messages from N1MM
stop_pattern = re.compile("\<stop\>")
azimuth_pattern = re.compile("\<goazi\>([0-9]+[.,][0-9]+)\<\/goazi\>")
frequency_pattern = re.compile("\<freqband\>([0-9]+[.,][0-9]+)\<\/freqband\>")

while (True):
    cmd = n1mm.recv(256)

    frequency_match = frequency_pattern.search(cmd)
    if (not frequency_match):
        continue

    frequency_band = frequency_match.group(1).replace(",", ".")
    azimuth_match = azimuth_pattern.search(cmd)

    #contains request for new position
    if (azimuth_match):
        azimuth = azimuth_match.group(1).replace(",", ".")
        rotors.send_azimuth_command(frequency_band, azimuth)

    #is a stop command
    if (stop_pattern.search(cmd)):
        rotors.send_stop_command(frequency_band)
