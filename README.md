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

Because of its general usefulness, we are looking into making this *aci_listify* filter more genericand part of the default Ansible filters.


## Role variables

The role accepts various variables, including:

- apic_host
- apic_username (defaults to 'admin')
- apic_password
- apic_use_proxy (defaults to false)
- apic_validate_certs (defaults to true)

The following is an example of a topology defined in your inventory you can use with this role:

```yaml
  aci_topology:
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
    aci_model_data: '{{ aci_topology }}'
```

## Notes
- Over time when more ACI modules are released with Ansible, we will swap the **aci_rest** calls with the high-level module calls.
- Feel free to add additional functionality and share it with us on Github !


## License
GPLv3
