#!/bin/bash

#install scripts to binary directory
echo "Copying executables to /usr/local/bin"
sudo cp rotctld-service-files/start-rotctld.sh /usr/local/bin/start-rotctld
sudo cp n1mm-rotctl/n1mm-rotctl.py /usr/local/bin/n1mm-rotctl

#install configuration
echo "Copying rotor configuration to /usr/local/etc"
sudo cp rotors.conf /usr/local/etc/

#install udev rules
echo "Copying udev rules to /etc/udev/rules.d"
sudo cp 70-la1k-symlinks.rules /etc/udev/rules.d/

#install service files
echo "Copy systemd service files to /etc/systemd/system"
sudo cp n1mm-rotctl/n1mm-rotctl.service /etc/systemd/system/
sudo cp rotctld-service-files/rotctld.service /etc/systemd/system/rotctld@.service

#reload systemd
sudo systemctl daemon-reload

#start n1mm receiver service
echo "Enabling and starting service n1mm-rotctl.service"
sudo systemctl enable n1mm-rotctl.service
sudo systemctl start n1mm-rotctl.service

#start rotctld services
rotors=$(cat rotors.conf | sed -rn 's/\[(.*)\]/\1/p')
for rotor in $rotors; do
	echo "Enabling and starting service rotctld@$rotor.service"
	sudo systemctl enable rotctld@$rotor
	sudo systemctl start rotctld@$rotor
done
