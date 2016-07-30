COMMANDS="sudo mv ~/Documents/grub /etc/default/grub;sudo update-grub;sudo reboot"

for node in $nodes; do
	sudo scp grub blue@"$node":/home/blue/Documents/
	ssh -t blue@"$node" "$COMMANDS"

done

