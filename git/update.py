#!/usr/bin/env python3
"""Update modul
 
Tento modul sluzi na zachytenie zapisu do vzdialeneho repozitara 
a nasledne generovanie konfliktu pred zapisom.
"""


import sys
import os
import subprocess
from pathlib import Path
import csv
from testmaker import TestMaker


def get_branch_from_ref(test_maker,ref):
    """Vyberie sa meno vetvy zo vstupu """

    ref += "-"
    return test_maker.check_something(ref,"refs/heads/","-")


def get_test_name(test_maker):
    """Zisti sa meno aktualne vykonavaneho testu """

    path_to_system = get_system_path(test_maker)
    path = path_to_system+"tests_files/actual_test.csv"
    test_name = ""
    if Path(path).exists():
        with open(path,"r",encoding = "ISO-8859-1") as csv_file:
            reader = csv.DictReader(csv_file,delimiter=';')

            for row in reader:
                if row['Test_Name'] != "":
                    test_name = row['Test_Name']
    else:
        print("File with actual test name dont exist.")
    return test_name


def read_conflict_info(test_maker,branch,test_name):
    """Nacitaju sa informacie o konfliktoch """

    array_from_csv = []
    is_make_conflict = ""
    path_to_system = get_system_path(test_maker)

    path = path_to_system +"tests_files/"+test_name+"/"+os.environ['USER']+"/conflict_info.csv"

    if Path(path).exists():
        with open(path,"r",encoding = "ISO-8859-1") as csv_file:
            reader = csv.DictReader(csv_file,delimiter=';')

            for row in reader:
                if row['Name'] != "" and row['Name'] == branch:
                    is_make_conflict = row['Is_Use']
                    task_id = row['Task_Id']
                help_array = []
                if row['Name'] != "" and row['Is_Use'] != "" and row['Task_Id'] != "":
                    help_array.append(row['Name'])
                    help_array.append(row['Is_Use'])
                    help_array.append(row['Task_Id'])
                array_from_csv.append(help_array)
                        
    else:
        print("File with conflict info dont exist.")

    return (is_make_conflict,task_id,array_from_csv)

def write_conflict_exist(test_maker,test_name,array):
    """Zapise sa, ktora vetva bola pouzita pri konflikte """

    path_to_system = get_system_path(test_maker)
    path = path_to_system +"tests_files/"+test_name+"/"+os.environ['USER']+"/conflict_info.csv"
    if Path(path).exists():
        with open(path,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Name','Is_Use','Task_Id']
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            for item in array:
                writer.writerow({ 'Name':item[0], 'Is_Use' : item[1], 'Task_Id' : item[2] })

def write_branch_for_conflict(test_maker,branch,test_name):
    """Zapise sa nazov aktualnej vetvy pre potreby vytvorenia konfliktu """

    path_to_system = get_system_path(test_maker)
    path = path_to_system +"tests_files/"+test_name+"/"+os.environ['USER']+"/actual_branch.csv"
    with open(path,"w",encoding = "ISO-8859-1") as csv_file:
        field_names = ['Branch','Print']
        writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
        writer.writeheader()
        writer.writerow({ 'Branch':branch, 'Print' : 'No' })


def change_branch_conflict_status(branch_to_change,array_with_conflict):
    """Zaznamena sa ze vetva pre konflikt bola uz pouzita """

    for branch in array_with_conflict:
        if branch[0] == branch_to_change:
            branch[1] = "Yes"
    return array_with_conflict


def have_print_conflict(test_maker,test_name):
    """Zisti ci sa ma vypisat info o konflikte (teda ci bol vytvoreny) """

    path_to_system = get_system_path(test_maker)
    path = path_to_system +"tests_files/"+test_name+"/"+os.environ['USER']+"/actual_branch.csv"
    have_print = ""
    if Path(path).exists():
        with open(path,"r",encoding = "ISO-8859-1") as csv_file:
            reader = csv.DictReader(csv_file,delimiter=';')

            for row in reader:
                if row['Print'] != "":
                    have_print = row['Print']
    else:
        print("File with actual branch csv not exist")

    if have_print == "Yes":
        return True
    else:
        return False


def print_conflict(branch):
    """Vypise sa info konflikte """
    
    print("\n! [rejected]        "+branch+" -> "+branch+" (fetch first)\n"
        +"hint: Updates were rejected because the remote contains work that you do\n"
        +"hint: not have locally. This is usually caused by another repository pushing\n"
        +"hint: to the same ref. You may want to first integrate the remote changes\n"
        +"hint: (e.g., 'git pull ...') before pushing again.\n"
        +"hint: See the 'Note about fast-forwards' in 'git push --help' for details.\n")


def remove_actual_branch_file(test_maker,test_name):
    """Vymaze sa subor z info o aktualnej vetve """

    path_to_system = get_system_path(test_maker)
    path = path_to_system +"tests_files/"+test_name+"/"+os.environ['USER']+"/actual_branch.csv"
    if Path(path).exists():
        os.system("rm -rf "+path)
    else:
        print("File with actual branch csv not exist")


def get_system_path(test_maker):
    """Zisti sa cesta k spustenemu skriptu """    

    path_to_system = os.path.realpath(__file__)
    return test_maker.check_something(path_to_system,"","update.py")


def main():

    if os.environ['USER'] != "root":
        test_maker = TestMaker()

        env_user = os.environ['USER']
        env_git_dir = os.environ['GIT_DIR']
        ref = sys.argv[1]
        branch = get_branch_from_ref(test_maker,ref)
        test_name = get_test_name(test_maker)
        array_with_conflict=[]
        (is_make_conflict,task_id,array_with_conflict) = read_conflict_info(test_maker,branch,test_name)

        if is_make_conflict == "No":

            write_branch_for_conflict(test_maker,branch,test_name)
            del os.environ['GIT_DIR']
            os.environ['USER'] = 'root'
            
            test_maker.change_students_repository(env_user,task_id,test_name)
            os.environ['USER'] = env_user
            os.environ['GIT_DIR'] = env_git_dir
            array_with_conflict = change_branch_conflict_status(branch,array_with_conflict)

            write_conflict_exist(test_maker,test_name,array_with_conflict)
            if have_print_conflict(test_maker,test_name):
                print_conflict(branch)
            remove_actual_branch_file(test_maker,test_name)


if __name__ == '__main__':
    main()