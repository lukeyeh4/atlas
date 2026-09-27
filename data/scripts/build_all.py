"""Rebuild every data file in order.

    python3 data/scripts/build_all.py                # everything except the population grid
    python3 data/scripts/build_all.py --population   # also rebuild it (~480 MB download)
"""
import runpy, sys
from pathlib import Path

HERE = Path(__file__).parent
STEPS = ['ember.py', 'country_wue.py', 'water_stress.py', 'pm25.py', 'country_inputs.py', 'subnational_grid.py',
         'locales.py', 'cells.py', 'node_profiles.py', 'node_types.py', 'research_raw.py', 'check_contract.py']
if '--population' in sys.argv:
    STEPS.insert(0, 'population_grid.py')      # before cells.py, which reads its grid

sys.path.insert(0, str(HERE))
for step in STEPS:
    print(f'== {step}')
    runpy.run_path(str(HERE / step), run_name='__main__')
