# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.private_key_path = "~/.ssh/id_ed25519"
  config.vm.provision "file", source: "~/.ssh/id_ed25519.pub", destination: "~/.ssh/authorized_keys"
  config.ssh.private_key_path = ["~/.ssh/id_ed25519", "~/.vagrant.d/insecure_private_key"]
  config.ssh.insert_key = false

  config.vm.define "alma" do |alma|
    alma.vm.box = "almalinux/9"
    alma.vm.box_version = "9.5.20241203"
    alma.vm.hostname = "alma" 
  end

  config.vm.define "debian" do |debian_config|
    debian_config.vm.box = "debian/bullseye64"
    debian_config.vm.box_version = "11.20241217.1"
    debian_config.vm.hostname = "debian"
  end
end
