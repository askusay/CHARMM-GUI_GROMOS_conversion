# CHARMM-GUI_GROMOS_conversion_tutorial
CHARMM-GUI creates systems ready for simulation but with charmm parameters, this can be converted to the amber format using `charmmlipid2amber.py`. Conversion to a united atom forcefield like `GROMOS-54A7` requires changing the number of atoms to a united atom represenation which is not supported by `charmmlipid2amber.py`.

The `convert_molecules.py` script developed here enables AA to UA conversion using templates, i.e. the included `charmm_to_gromos.yaml` file, see figure below:

![](ua_aa_conv.png)
