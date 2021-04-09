# Copyright: (c) 2020-2021, Tilmann Boess <tilmann.boess@hr.de>
# Based on: (c) 2017, Ramses Smeyers <rsmeyers@cisco.com>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
This is an alternative filter to the original 'aci_listify' in 'aci.py'.
It is useful if your inventory data / variable definitions are not organized in
alternating dicts and lists down your tree."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

def Lister(Dict, *Keys):
  """Extract key/value data from ACI-model object tree.
The object tree may contain nested dicts and lists in any order.
The keys must match dict names along a path in this tree down to a dict that
contains at least 1 key/value pair.
Along this path all key/value pairs for all keys given are fetched.
Args:
- Dict (dict): object tree.
- *Keys: key names to look for in 'Dict' in hierarchical order (the keys must
  form a path in the object tree).
– You can append a regex to each key (separated by an =–sign). Only keys
  whose name-attribute matches the regex will be included in the result.
  If the regex is omitted, all keys will be included (backwards compatible).
  Examples:
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
      - Name: 101
        port:
        - Name: 1
          type:
          - Name: switch_port
      - Name: 101
        port:
        - Name: 2
          type:
          - Name: port_channel
    (and so on for all leaf-switches and ports)
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
          - leafid.Name: '10.'
            leafid_port_Name: '1'
          - leafid.Name: '203'
            leafid_port_Name: '42'
    The dict 'portlist' need not be specified here as task variable.
    You can provide it as extra var on the command line and thus specify
    dynamically which ports shall be configured.
Returns:
- list of dicts (key/value-pairs); given keys are concatenated with '_' to form
  a single key. Example: ('tenant' , 'app' , 'epg') results in 'tenant_app_epg'.
"""
  # Name of the attribute used as «Name». We use uppercase «Name» to
  # let it appear 1st if YAML/JSON files are sorted by keys.
  # Change it to your liking.
  NameAttr = 'Name'
  R_Value = re.compile('([^=]+)=(.+)')
  # KeyList will be a copy of the initial list «Keys».
  KeyList = []
  # List of regex to match the name attributes.
  RegexList = []
  for K in Keys:
    Match = R_Value.fullmatch(K)
    if Match:
      KeyList.append(Match.group(1))
      RegexList.append(re.compile(Match.group(2)))
    else:
      KeyList.append(K)
      RegexList.append(None)

  def Worker(Item, KeyList, RegexList, Depth=-1, Result=[], Cache={}, Prefix=''):
    """Recursive inner function to encapsulate the internal arguments.
Args:
- Item: current object in tree for key search (depends on value of 'Depth').
- KeyList (list): list of keys.
– RegexList (list): list of regex objects.
- Depth (int): index (corresponding to depth in object tree) of key in key list.
- Result (list): current result list of key/value-pairs.
- Cache (dict): collects key/value pairs common for all items in result list.
- Prefix (str): current prefix for key list in result.
"""
    if isinstance(Item, dict):
      if not Depth == -1:
        Prefix = ''.join((Prefix, KeyList[Depth], '_'))
      # For each named node in the tree, count one level up.
      Depth +=1
      # List of attributes that contain flat values (neither dict nor list).
      FlatAttribList = []
      for SubItem in Item:
        if not isinstance(Item[SubItem], dict) and not isinstance(Item[SubItem], list):
          # Flat key/value pair.
          # Cache holds the pathed keys (build from the key list).
          # Each recursive call gets its own copy.
          Cache['%s%s' %(Prefix, SubItem)] = Item[SubItem]
          # All key/value pairs are evaluated before dicts and lists.
          # Otherwise, some attributes might not be transferred from the
          # cache to the result list.
          FlatAttribList.append(SubItem)
      for SubItem in FlatAttribList:
        # Delete flat key/value pairs (already evalutated in previous loop)
        # so that remaining Items are either list or dict.
        del Item[SubItem]
      for SubItem in Item:
        if Depth < len(KeyList) and SubItem == KeyList[Depth]:
          # Not at end of key list and Item matches current key.
          Result = Worker(Item[SubItem], KeyList, RegexList, Depth, Result, Cache.copy(), Prefix)
      if Depth == len(KeyList):
        # At end of key list: transfer cache to result list.
        Result.append(Cache)
    elif isinstance(Item, list):
      # For lists, look deeper without increasing the depth.
      for ListItem in Item:
        if RegexList[Depth] != None and Depth < len(RegexList) and isinstance(ListItem, dict) and not RegexList[Depth].fullmatch(str(ListItem.get(NameAttr, ''))):
          # If regex was specified and the NameAttr does not match, do
          # not follow the path but continue with next item. Also a
          # non-existing NameAttr attribute is interpreted as non-match.
          continue
        Result = Worker(ListItem, KeyList, RegexList, Depth, Result, Cache.copy(), Prefix)
    return Result
    # End of inner function

  return Worker(Dict, KeyList, RegexList)

class FilterModule(object):
  """Ansible core jinja2 filters"""

  def filters(self):
    return { 'aci_listify2': Lister }
