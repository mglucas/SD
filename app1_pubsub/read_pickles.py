import pickle
import os
from pathlib import Path
from rich import print


def pickleload(name, direct_path=None):
    """
    Description: simple formalization of the function "load" from the library
                 pickle. Open file that has the given name and load its data.
    
    Parameters:
    - name (string): string name of the file that will be opened and loaded;
    - direct_path (string): path for the exact location where the pickle should
                            be loaded from.

    Returns:
    - loaded_data (undefined): data retreived from pickle file.
    """

    with open(f"{name}.pickle", 'rb') as handle:
        loaded_data = pickle.load(handle)
    if loaded_data == None:
        return []
    return loaded_data


print("==================================")
# if Path("clients.pickle").is_file():
#     print(pickleload("clients"))
# if Path("current_id.pickle").is_file():
#     print(pickleload("current_id"))
# if Path("requests.pickle").is_file():
#     print(pickleload("requests"))
# if Path("rides.pickle").is_file():
#      print(pickleload("rides"))
if Path("a_bank_account.pickle").is_file():
     print(pickleload("a_bank_account"))
if Path("b_bank_account.pickle").is_file():
     print(pickleload("b_bank_account"))
if Path("c_bank_account.pickle").is_file():
     print(pickleload("c_bank_account"))
print("==================================")