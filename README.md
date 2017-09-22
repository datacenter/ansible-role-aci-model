# Ansible Role: aci-model
A comprehensive Ansible role to model and deploy Cisco ACI fabrics.

This role provides an abstraction layer that is convenient to use. By providing your required configuration (a structured dataset) in your inventory this role will perform the needed actions to ensure that configuration is deployd on your ACI infrastructure.

Using this role you can easily set up demo environment, maintain a lab or use it as the basis for your in-house ACI infrastructure. It can help you understand how ACI works while prototyping and testing. No prior Ansible or ACI knowledge is required to get started.


## Requirements
This role requires the **aci_rest** module and the standard set of ACI modules from Ansible v2.4.


## Installation

### Install the aci-model role
There are two ways you can test this role:

 1. Installing it by cloning the Github repository

        git clone https://github.com/datacenter/ansible-role-aci-model datacenter.aci-model

 2. Install it using the ansible-galaxy command

        ansible-galaxy install datacenter.aci-model


### Install the aci filter plugin
In order to work with the provided ACI topology, a custom Jinja2 filter (*aci_listify*) is needed.
You need to configure your Ansible to find this Jinja2 filter. There are two ways to do this:

 1. Configure Ansible so it looks for the custom aci filter plugin:

      ```ini
      filter_plugin = /home/ansible/datacenter.aci-model/plugins/filter
      ```

 2. Copy the filter plugin (*plugins/filter/aci.py*) into your designated filter plugin directory

Because of its general usefulness, we are looking into making this *aci_listify* filter more generic and make it part of the default Ansible filters.


## Using the example playbook

### Configure your APIC host and credentials
Look inside the example inventory and provide the needed information.
Only the first APIC is being use by the playbook, so you don't need more than one.

#### Role variables
The role accepts various variables, including:

- apic_host
- apic_username (defaults to 'admin')
- apic_password

- apic_use_proxy (defaults to false)
- apic_validate_certs (defaults to true)

You can configure these as part of your host variables, or group variables.

### Ensure the playbook can find your datacenter.aci-model role
If you cloned it from Github, ensure you cloned it to a directory named datacenter.aci-model.
Otherwise the playbook will not find the role with name "datacenter.aci-model".

If you installed the role from Galaxy, you should be fine to use the examples from Github.

### Running the example playbook
Run the following command using Ansible v2.4:

    ansible-playbook -i example-inventory.yml example-playbook.yml -v

The first time it will deploy that configuration on your ACI infrastructure.

You can make modifications and run it again as often as you like to modify the existing configuration.


## Examples

### Example inventory
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

### Example playbook

```yaml
- hosts: *apic1
  gather_facts: no
  roles:
  - role: datacenter.aci-model
    aci_model_data: '{{ aci_topology }}'
```

## Notes
- Over time when more ACI modules are released with Ansible, we will swap the **aci_rest** calls with the high-level module calls.
- Feel free to add additional functionality and share it with us on Github !


## License
GPLv3
