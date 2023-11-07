# Copyright: (c) 2020-2023, Tilmann Boess <tilmann.boess@hr.de>
# Based on: (c) 2017, Ramses Smeyers <rsmeyers@cisco.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def listify(d, *keys):
    """Extract key/value data from ACI-model object tree.
The object tree must have the following structure in order to find matches: dict
at top-level, list at 2nd level and then alternating dicts and lists.
The keys must match dict names along a path in this tree down to dict that
contains at least 1 key/value pair.
Along this path all key/value pairs for all keys given are fetched.
Args:
- d (dict): object tree.
- *keys: key names to look for in ' d'  in hierarchical order (the keys must form
    a path in the object tree).
Returns:
- list of dicts (key/value-pairs); given keys are concatenated with '_' to form
    a single key. Example: ('tenant' , 'app' , 'epg') results in 'tenant_app_epg'.
"""

    def listify_worker(d, keys, depth=0, result=[], cache={}, prefix=''):
        """Recursive inner function to encapsulate the internal arguments.
Args:
- d (dict): subtree of objects for key search (depends on value of ' depth' ).
- keys (list): list of keys.
- depth (int): index (corresponding to depth in object tree) of key in key list.
- result (list): current result list of key/value-pairs.
- cache (dict): collects key/value pairs common for all items in result list.
- prefix (str): current prefix for key list in result.
"""
        prefix = ''.join((prefix, keys[depth], '_'))
        if keys[depth] in d:
            # At level of dict.
            for item in d[keys[depth]]:
                # One level below: Loop thru the list in this dict. If 'd[keys[depth]]' is a dict, the next test will fail and the recursion ends.
                if isinstance(item, dict):
                    # 'cache_work' holds all key/value pairs along the path.
                    cache_work = cache.copy()
                    for k, v in item.items():
                        # Two levels below: Loop thru the dict.
                        if not isinstance(v, (dict, list)):
                            # Key/value pair found: add value 'v' to cache for key 'k'.
                            cache_work[''.join((prefix, k))] = v
                        elif isinstance(v, list):
                            # Support a list of scalars as attribute value.
                            for listItem in v:
                                if isinstance(listItem, (dict, list)):
                                    break
                            else:
                                cache_work[''.join((prefix, k))] = v
                    if len(keys)-1 == depth:
                        # Max. depth reached.
                        result.append(cache_work)
                    else:
                        # Lookup next key in the dict below.
                        nextkey = keys[depth+1]
                        if nextkey in item and isinstance(item[nextkey], list):
                            # It's useless to test for dict here because the recursion will end in the next level.
                            result = listify_worker({nextkey: item[nextkey]}, keys, depth+1, result, cache_work, prefix)
        return result
        # End of inner function

    return listify_worker(d, keys)


class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return {
            'aci_listify': listify
        }
