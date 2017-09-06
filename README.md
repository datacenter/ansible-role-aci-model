# Ansible Role: aci_model

A comprehensive Ansible role to model and deploy Cisco ACI fabrics

## Requirements

This role requires the **aci_rest** module and a standard set of ACI modules from Ansible v2.4.


## Role variables

Available variables are listed below, along with default values:

    aci_model_data:
      
## Example playbook

    - hosts: *apic1
      roles:
      - role: aci_model
        aci_model_data: '{{ your.inventory.aci_topology }}'

## License
GPLv3
