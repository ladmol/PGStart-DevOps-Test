.PHONY: acheck
.PHONY: arun

acheck:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml --check 

arun:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml

arun_alma:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml -l alma

arun_debian:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml -l debian