#!/bin/bash

#Attempt to obtain current position from all rotors defined in /usr/local/etc/rotors.conf

rotorconfig="/usr/local/etc/rotors.conf"
rotors=$(cat $rotorconfig | sed -rn 's/\[(.*)\]/\1/p')
for rotor in $rotors; do
	port=$(cat $rotorconfig | sed -rn "/\[$rotor\]/,/\[/p" | sed -rn "s/^rotctld_port=(.*)/\1/p")
	echo "$rotor (localhost:$port):"
	rotctl -m 2 -r localhost:$port p
	echo ""
done
