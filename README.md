# CHARMM-GUI_GROMOS_conversion_tutorial
CHARMM-GUI creates systems ready for simulation but with charmm parameters, this can be converted to the amber format using `charmmlipid2amber.py`. Conversion to a united atom forcefield like `GROMOS-54A7` requires changing the number of atoms to a united atom represenation which is not supported by `charmmlipid2amber.py`.

The `convert_molecules.py` script developed here enables all-atom (AA) to united-atom (UA) conversion using templates, i.e. the included `charmm_to_gromos.yaml` file. The code does have checkes in place, but double check your conversions and pay attention to any warning about atom names emitted from grompp!

This tool also enables conversion of AA ligand pdb files to UA ATB files. I.e. if you have done ligand docking in all atom represenation and want to change the atom/residue names of the docked ligand based on ATB files.

![](aa_ua_conv.png)

## Tutorial
*Files for this tutorial may be found in XXX*
* Here I have generated a small CHARMM-GUI system `step5_input.pdb` (nAChR with nicotine bound and embedded in POPC membrane)
* The `step5_assembly.str`
* The `NCT_prot_het.pdb` file was created by processing the protein through [`pdb2gmx`](https://manual.gromacs.org/documentation/2021/onlinehelp/gmx-pdb2gmx.html) and adding the ligand (nicotine) to the file.
    * Used the GROMOS-54A7 forcefield for the ligand 
    * Generated parameters for nicotine using ATB, [they can be found here](https://atb.uq.edu.au/molecule.py?molid=703425)

### Inserting the UA-protein into the CHARMM-GUI system
1. Load both `step5_input.pdb` and `NCT_prot_het.pdb` into VMD (assuming they have molid 0 1 respectively)
2. Align the protein from `NCT_prot_het` on `step5_input`, commands to be entered in `TkConsole`
```
set ref [atomselect 0 "protein and name CA"]
set target [atomselect 1 "protein and name CA"]
set all [atomselect 1 all]
$all move [measure fit $target $ref]
```
3. Optional step, if your protein is not centered in the box, i.e. poking out the top, use the [`shift_solvent.tcl`](https://github.com/askusay/MD_box_fixer) vmd scritpt to fix it
4. Save the adjusted `NCT_prot_het` structure -> `NCT_prot_aln.pdb`
5. Save the `step5_input` structure without the protein or ligand atoms -> `step5_mem_ion.pdb`:
    * Example selection: `not (segid "PRO[A-Z]" "HET[A-Z]")`
6. Combine the `NCT_prot_aln.pdb` and `step5_mem_ion.pdb` files:

```
cat NCT_prot_aln.pdb step5_mem_ion.pdb > NCT_comb.pdb
```
**IMPORTANT:** remove the **END** and **CRYST1** lines between the atoms in the joined files!



### Running `convert_molecules.py`:
```
convert_molecules.py NCT_comb.pdb NCT_comb_conv.pdb charmm_to_gromos.yaml
```
*Note*:

POPC conversion corresponds with ([Poger et. al 2009](https://pubs.acs.org/doi/abs/10.1021/ct900487a))



### Running `GMX editconf`
*[GMX editconf](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-editconf.html) is required to set the box dimentions for running PBC simulations*
* Extract info about system size from `step5_assembly.str`: `A length: 111.618775, B length: 111.618775, C length: 150.889`
    * *If you have used the `shift_solvent.tcl` in step 4, \
      add ~2 angstrom padding to the vertical C dimention, i.e. 150.889 -> 152.889* 
* For rectangular systems:
```
gmx editconf -f NCT_comb_conv.pdb -o NCT_comb_box.pdb -box 11.1522525 11.1522525 15.2889
```
* For hexagonal (triclinic) boxes 
```
gmx editconf -f NCT_comb_conv.pdb -o NCT_comb_box.pdb -box 11.1522525 11.1522525 15.2889 -angles 90 90 60 -bt triclinic
```

### Notes on creating templates:
Each line in the `conversions` is formatted as `[source_numbering, source, template]`
1. Open the united-atom and AA pdb files in a visualisation software like PyMOL and label the atoms by name
   * Helps to use [`grid mode`](https://pymolwiki.org/index.php/Grid_mode)
3. Copy the atom and residue names from the united-atom pdb file to the `template` column
    * Helps to use code editors like VS code with column selection mode
    ![](giphy.gif)
2. Copy the corresponding atom/residue names from the AA pdb file to the `source` column
3. Copy the corresponding atomic index from the AA pdb file to the `source_numbering` column 
    * **IMPORTANT:** AA file must have atoms numbered from **1**
