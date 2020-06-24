# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
 # The most common configuration options are documented and commented below.
 # For a complete reference, please see the online documentation at
 # https://docs.vagrantup.com.

 # Every Vagrant development environment requires a box. You can search for
 # boxes at https://vagrantcloud.com/search.
 # The image is pinned to a specific version so that things don't break in case changes are made to the base image.
 config.vm.box = "ubuntu/bionic64"
 config.vm.box_version = "~> 20200304.0.0"

 # Map port from local (host) machine to port on the development server (guest)
 config.vm.network "forwarded_port", guest: 8000, host: 8000

 # Defines how scripts are run when server is first created.
 # The autoupdates are disabled as they'd otherwise conflict with "sudo apt-get update" when run on Ubuntu
 config.vm.provision "shell", inline: <<-SHELL
   systemctl disable apt-daily.service
   systemctl disable apt-daily.timer

   # Update local repo with all available packages, and install python3-venv and zip
   sudo apt-get update
   sudo apt-get install -y python3-venv zip

   # Create bash alises file and set Python3 to be the default Python version for the vagrant user
   touch /home/vagrant/.bash_aliases
   if ! grep -q PYTHON_ALIAS_ADDED /home/vagrant/.bash_aliases; then
     echo "# PYTHON_ALIAS_ADDED" >> /home/vagrant/.bash_aliases
     echo "alias python='python3'" >> /home/vagrant/.bash_aliases
   fi
 SHELL
end
