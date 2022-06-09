# Short script to save instance information to CSV for inclusion in
# documentation page.

# Must be run from src directory.


from stockpyl.instances import _save_summary_to_csv

_save_summary_to_csv('../docs/aux_files/named_instances.csv')