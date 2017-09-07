# Ansible Role: aci-model

A comprehensive Ansible role to model and deploy Cisco ACI fabrics


## Requirements

This role requires the **aci_rest** module and a standard set of ACI modules from Ansible v2.4.

In order to work with the provided ACI topology, a custom Jinja2 filter (*aci_listify*) is needed.
You need to configure your Ansible to find this Jinja2 filter. There are two ways to do this:

 1. Configure Ansible so it looks for the custom filter plugin:

      ```ini
      filter_plugin = /home/ansible/datacenter.aci-model/plugins/filter
      ```

 2. Copy the filter plugin (*plugins/filter/aci.py*) into your designated filter plugin directory


## Role variables

The following is an example of an inventory for this role:

```yaml
aci_model_data:
  tenant:
  - name: Example99
    description: Example99
    app:
    - name: Billing
      epg:
      - name: web
        bd: web_bd
        contract:
        - name: internet
          type: consumer
        - name: web_app
          type: consumer
      - name: app
        bd: app_bd
        contract:
        - name: web_app
          type: provider
  bd:
  - name: app_bd
    subnet:
    - name: 10.10.10.1
      mask: 24
      scope: private
    vrf: Example99
  - name: web_bd
    subnet:
    - name: 20.20.20.1
      mask: 24
      scope: public
    vrf: Example99
  vrf:
  - name: Example99
  contract:
  - name: internet
    scope: tenant
    subject:
    - name: internet
      filter: default
  - name: web_app
    scope: tenant
    subject:
    - name: web_app
      filter: default
```
A more comprehensive example is available from: [example-inventory.yaml](example-inventory.yaml)


## Example playbook

```yaml
- hosts: *apic1
  gather_facts: no
  roles:
  - role: aci-model
    aci_model_data: '{{ inventory.aci_topology }}'
```

## Notes

- Over time more ACI modules will become available and this role will be adapted to work
  using those newer ACI modules, replacing the low-level **aci_rest** tasks.


## License
GPLv3
