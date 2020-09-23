# Copyright: (c) 2020, Tilmann Boess <tilmann.boess@hr.de>
# Based on: (c) 2017, Ramses Smeyers <rsmeyers@cisco.com>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
This is an alternative filter to the original 'aci_listify' in 'aci.py'.
It is useful if your inventory data / variable definitions are not organized in
alternating dicts and lists down your tree."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def Lister(Dict, *Keys):
  """Extract key/value data from ACI-model object tree.
The object tree may contain nested dicts and lists in any order.
The keys must match dict names along a path in this tree down to a dict that
contains at least 1 key/value pair.
Along this path all key/value pairs for all keys given are fetched.
Args:
- Dict (dict): object tree.
- * Keys: key names to look for in 'Dict'  in hierarchical order (the keys must
  form a path in the object tree).
Returns:
- list of dicts (key/value-pairs); given keys are concatenated with '_' to form
  a single key. Example: ('tenant' , 'app' , 'epg') results in 'tenant_app_epg'.
"""

  def Worker(Item, Keys, Depth=-1, Result=[], Cache={}, Prefix=''):
    """Recursive inner function to encapsulate the internal arguments.
Args:
- Item: current object in tree for key search (depends on value of 'Depth').
- Keys (list): list of keys.
- Depth (int): index (corresponding to depth in object tree) of key in key list.
- Result (list): current result list of key/value-pairs.
- Cache (dict): collects key/value pairs common for all items in result list.
- Prefix (str): current prefix for key list in result.
"""
    if isinstance(Item, dict):
      if not Depth == -1:
        Prefix = ''.join((Prefix, Keys[Depth], '_'))
      # For each named node in the tree, count one level up.
      Depth +=1
      for SubItem in Item:
        if not isinstance(Item[SubItem], dict) and not isinstance(Item[SubItem], list):
          # Path end: key/value pair.
          # Cache holds the pathed keys (build from the key list).
          # Each recursive call gets its own copy.
          Cache['%s%s' %(Prefix, SubItem)] = Item[SubItem]
        elif Depth < len(Keys) and SubItem == Keys[Depth]:
          # Neither at end of key list nor at end of path.
          Worker(Item[SubItem], Keys, Depth, Result, Cache.copy(), Prefix)
      if Depth == len(Keys):
        # Path length exhausted, do not look deeper.
        Result.append(Cache)
    elif isinstance(Item, list):
      # For lists, look deeper without increasing the depth.
      for ListItem in Item:
        Worker(ListItem, Keys, Depth, Result, Cache.copy(), Prefix)
    return Result
    # End of inner function

  return Worker(Dict, Keys)

class FilterModule(object):
  """Ansible core jinja2 filters"""

  def filters(self):
    return { 'aci_listify2': Lister }
