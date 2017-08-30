#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 [config file] [rotor name]"
	exit
fi

filename="$1"
rotorname="$2"
pid=$$

# Obtain option from config file in ini-style format:
#
#  [section]
#  ...
#  option=value
#  ...
#
# Run using get_conf_option $option. Filename and section from which
# config is extracted is defined above in $filename and $rotorname,
# respectively.
function get_conf_option()
{
	option="$1"
	value=$(cat $filename | sed -rn "/\[$rotorname\]/,/\[/p" | sed -rn "s/^$option=(.*)/\1/p")
	if [[ -z $value ]]; then
		echo "Option '$option' not defined for '$rotorname' in config file." >&2
		kill -9 $pid
	fi
	echo $value
}

#read rotctld settings from config file
port=$(get_conf_option "rotctld_port")
device=$(get_conf_option "device")
options=$(get_conf_option "rotctld_options")
model=$(get_conf_option "rotctld_model")

#start rotctld
rotctld -t $port -m $model -r $device $options
