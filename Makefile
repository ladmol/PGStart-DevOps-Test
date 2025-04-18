.PHONY: acheck
.PHONY: arun

acheck:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml --check 

arun:
	ansible-playbook -i ./ansible/inventory/hosts.txt ./ansible/playbook.yml

