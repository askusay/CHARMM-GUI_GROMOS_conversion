#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 askusay
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import numpy as np
import yaml

def make_filename(filename):
    '''Checks to see if desired file exists, if so it is renamed
    Can provide filename with or without directory i.e. "filename", "../filename" and "/directory/filename"
    If the directory does not exist then it will be made 
    '''
    
    base, file = os.path.split(filename)
    
    # check if file exists
    '''This secion is adapted from https://github.com/csblab/md_scripts/blob/master/openmm/amberff/_utils.py'''
    if os.path.isfile(filename):
        fname = filename
        num = 1
        
        while True:
            file = '#{}.{}#'.format(file, num)
            # make complete path
            filename = os.path.join(base, file)
            if os.path.isfile(filename):
                num += 1
            else: 
                os.rename(fname, filename)
                break
        return fname
    
    # if the file does not exists, then check if dir exits
    else: 
    # ignore if base is current dir '.' - previous dir '..' - nothing ''
        if not base in ['.', '..', '']:
        # Make if necessary
            if not os.path.isdir(base):
                os.makedirs(base)
            
    return filename

def fix_atb(file_in, file_out, template):
    
    with open(template) as file:
        convert_mols = yaml.load(file, Loader=yaml.FullLoader)
        
    for i, v in convert_mols.items():
        assert type(v["conversions"]) == list, 'Each conversions line must be formatted like this: - [source_numbering, source, template]'
        assert all([len(j) == 3 for j in v["conversions"]]), f'"conversions" of {i} in {template} does not appear to be formatted correctly,\nEach conversions line must be formatted like this: - [source_numbering, source, template]'
        if v['atoms'] > 1:
            as_array = np.array(convert_mols[i]['conversions'])
            v['map']  = as_array[:,0].astype(int) - 1
    
    with open(file_in) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    content_iter = iter(content)
    fixed = ""
    
    for i in content_iter:
        # limit search to 1 space around residue name in PDB file
        res = i[17:21].strip()
        if i.startswith('TER'):
            fixed += i + '\n'
            continue
            
        if res in convert_mols.keys():
            no  = convert_mols[res]['atoms']
            tmp = convert_mols[res]['conversions']
            assert len(tmp[0]) == 3, ''
            if no == 1:
                tmp = tmp[0]
                replaced = i.replace(tmp[1],tmp[2]) 
                if tmp[1] != tmp[2]:
                    assert i != replaced, f'Replacement failed for {i}\nsource: {tmp[1]}, target: {tmp[2]}\nafter replacement:{replaced}'
                fixed += replaced + "\n"
                    
            else:   
                atm_map = convert_mols[res]['map']
                lig = [i]
                [lig.append(next(content_iter)) for _ in range(1,no)] # skip n lines and append
                            
                np_lig = np.array(lig)
                np_lig_filter = np_lig[atm_map]
                
                assert len(np_lig_filter) == len(tmp), ''
                
                for current, t in zip(np_lig_filter, tmp):
                    replaced = current.replace(t[1],t[2])
                    if t[1] != t[2]:
                        assert current != replaced, f'Replacement failed for {i}\nsource: {t[1]}, target: {t[2]}\nafter replacement:{replaced}'
                    fixed += replaced + "\n"
                
        else:
            fixed += i + '\n'

    with open(make_filename(file_out), 'w+') as f:
        f.write(fixed)
        
    return 

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pdb_in', help='Input PDB file')
    parser.add_argument('pdb_out', help='Output PDB file')
    parser.add_argument('template', help='template yaml file i.e. "mol_dict.yaml"')

    args = parser.parse_args()

    fix_atb(args.pdb_in, args.pdb_out, args.template)