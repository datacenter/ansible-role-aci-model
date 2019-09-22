# Copyright: (c) 2017, Ramses Smeyers <rsmeyers@cisco.com>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

def listify(d, *keys):
    return listify_worker(d, keys, 0, [], {}, '')

def listify_worker(d, keys, depth, result, cache, prefix):
    prefix += keys[depth] + '_'

    if keys[depth] in d:
        for item in d[keys[depth]]:
            cache_work = cache.copy()
            if isinstance(item, dict):
                for k,v in item.items():
                    if not isinstance(v, dict) and not isinstance(v, list):
                        cache_key = prefix + k
                        cache_value = v
                        cache_work[cache_key] = cache_value

                if len(keys)-1 == depth :
                    result.append(cache_work)
                else:
                    for k,v in item.items():
                        if k == keys[depth+1]:
                            if isinstance(v, dict) or isinstance(v, list):
                                result = listify_worker({k:v}, keys, depth+1, result, cache_work, prefix)
    return result

class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return {
            'aci_listify': listify,
        }
