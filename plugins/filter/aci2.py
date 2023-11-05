# Copyright: (c) 2020-2022, Tilmann Boess <tilmann.boess@hr.de>
# Based on: (c) 2017, Ramses Smeyers <rsmeyers@cisco.com>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
This is an alternative filter to the original 'aci_listify' in 'aci.py'.
The instances (e.g. tenant, vrf, leafid, …) can be organized in a dict as
well as in a list. If you need to lookup instances directly (e.g. by other
filters), it might be useful to organize your inventory in dicts instead
of lists.

*** Examples ***
1. Simple static specification:
  loop: "{{ aci_topology|aci_listify2('access_policy', 'interface_policy_profile=.+998', 'interface_selector') }}"
All paths in the output match interface policy profiles that end in «998».
E.g. interface selectors below a non-matching interface policy profile
will be suppressed from the output.
2. Dynamic specification:
  loop: "{{ LEAFID_ROOT|aci_listify2(leaf_match, port_match, 'type=switch_port') }}"
  vars:
    leaf_match: "leafid={{ outer.leafid_Name }}"
    port_match: "port={{ outer.leafid_port_Name }}"
Here the regex's for the leafid and the port are determined at runtime in an
outer task. The outer task sets the dict 'outer' and this dict is referenced
here.
'LEAFID_ROOT' is the dict in which to look for the following hierarchy:
  leafid:
  # leafid 101: all instances organized in lists.
  - Name: 101
    port:
    - Name: 1
      type:
      - Name: vpc
    - Name: 2
      type:
      - Name: port_channel
    - Name: 3
      type:
      - Name: switch_port
  - Name: 102
    # leafid 102: organized in dicts and lists.
    port:
      # port instances: dict
      1:
        Name: 1
        type:
          # type instances: dict
          vpc:
            Name: vpc
      2:
        Name: 2
        type:
          # type instances: dict
          port_channel:
            Name: port_channel
      4:
        Name: 4
        type:
        # type instances: list
        - Name: switch_port
( … and so on for all leaf-switches and ports …)
This matches only if:
* leafid matches the leafid delivered by the outer task.
* port matches the port delivered by the outer task.
* The port shall be configured as a simple switchport (not a channel).
The outer task could be:
  - name: "example outer task"
    include_tasks:
      file: inner.yaml
    loop: "{{ portlist }}"
    loop_control:
      loop_var: outer
    vars:
      portlist:
      - leafid_Name: '10.'
        leafid_port_Name: '3'
      - leafid_Name: '.0.'
        leafid_port_Name: '(2|4)'
The dict 'portlist' need not be specified here as task variable.
You can provide it as extra var on the command line and thus specify
dynamically which ports shall be configured.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re


def def_filter():
    """Outer function that defines the filter and encapsulates initialization of variables.
"""
    # Name of the attribute used as «Name». We use uppercase «Name» to
    # let it appear 1st if YAML/JSON files are sorted by keys.
    # Change it to your liking.
    nameAttr = 'Name'
    # Regex to separate object and instance names.
    rValue = re.compile('([^=]+)=(.*)')

    def lister(myDict, *myKeys):
        """Extract key/value data from ACI-model object tree.
The keys must match dict names along a path in this tree down to a dict that
contains at least 1 key/value pair.
Along this path all key/value pairs for all keys given are fetched.
Args:
* myDict (dict): object tree.
* *myKeys: key names to look for in 'myDict' in hierarchical order (the keys
  must form a path in the object tree).
* You can append a regex to each key (separated by «=»). Only keys
  whose name-attribute matches the regex will be included in the result.
  If the regex is omitted, all keys will be included (backwards compatible).
Returns:
* list of dicts (key/value-pairs); given keys are concatenated with '_' to form
  a single key. Example: ('tenant' , 'app' , 'epg') results in 'tenant_app_epg'.
"""
        # keyList will be a copy of the initial list «myKeys».
        keyList = []
        # List of regex to match the name attributes.
        regexList = []
        for K in myKeys:
            match = rValue.fullmatch(K)
            if match:
                keyList.append(match.group(1))
                regexList.append(re.compile(match.group(2)))
            else:
                keyList.append(K)
                regexList.append(None)

        def worker(itemList, depth, result, cache, prefix):
            """Inner function for instance evaluation.
Args:
* itemList (list): current instance list in tree (list of dicts, each item
  is an ACI object).
* depth (int): index (corresponding to depth in object tree) of key in key list.
* result (list): current result list of key/value-pairs.
* cache (dict): collects key/value pairs common for all items in result list.
* prefix (str): current prefix for key list in result.
"""
            for item in itemList:
                # Save name attribute for later usage.
                # If name attribute is missing, set to None.
                name = str(item.get(nameAttr, None))
                # cache holds the pathed keys (build from the key list).
                # Each recursive call gets its own copy.
                subcache = cache.copy()
                for subItem in list(item.keys()):
                    if not isinstance(item[subItem], (dict, list)):
                        # Flat key/value pair.
                        subcache['%s%s' % (prefix, subItem)] = item[subItem]
                        # All key/value pairs are evaluated before dicts and lists.
                        # Otherwise, some attributes might not be transferred from the
                        # cache to the result list.
                    elif isinstance(item[subItem], list):
                        # Support a list of scalars as attribute value.
                        for listItem in item[subItem]:
                            if isinstance(listItem, (dict, list)):
                                break
                        else:
                            subcache['%s%s' % (prefix, subItem)] = item[subItem]
                if regexList[depth] is not None and (name is None or not regexList[depth].fullmatch(name)):
                    # If regex was specified and the nameAttr does not match, do
                    # not follow the path but continue with next item. Also a
                    # non-existing nameAttr attribute is interpreted as non-match.
                    continue
                result = finder(item, depth, result, subcache, prefix)
            return result

        def finder(objDict, depth=-1, result=None, cache=None, prefix=''):
            """Inner function for tree traversal.
* objDict (dict): current subtree, top key is name of an ACI object type.
* depth (int): index (corresponding to depth in object tree) of key in key list.
* result (list): current result list of key/value-pairs.
* cache (dict): collects key/value pairs common for all items in result list.
* prefix (str): current prefix for key list in result.
"""
            if result is None:
                result = []
            if cache is None:
                cache = {}
            depth += 1
            if depth == len(keyList):
                # At end of key list: transfer cache to result list.
                result.append(cache)
            else:
                prefix = ''.join((prefix, keyList[depth], '_'))
                # Check if object type is in tree at given depth.
                if keyList[depth] in objDict:
                    # Prepare item list. ACI objects may be stored as list or dict.
                    if isinstance(objDict[keyList[depth]], list):
                        itemList = objDict[keyList[depth]]
                    elif isinstance(objDict[keyList[depth]], dict):
                        itemList = list(objDict[keyList[depth]].values())
                    else:
                        # Neither dict nor list – return to upper level.
                        return result
                    result = worker(itemList, depth, result, cache.copy(), prefix)
            return result

        # End of function: lister
        return finder(myDict)

    # End of function: def_filter
    return lister


class FilterModule(object):
    """Jinja2 filters for Ansible."""

    def filters(self):
        """Name the filter: aci_listify2"""
        return {'aci_listify2': def_filter()}
