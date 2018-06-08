"""Git_maker modul

Metody pre vygenerovanie, vytvorenie a kontrolu zadania uloh Git systemu.
"""

import csv
from parser import Parser
from pathlib import Path
import random
import os
import re
import git
import shutil
import filecmp

class GitMaker:

    parser = Parser("")

    def __init__(self,args):
        self.args = args
        self.text = "default"
        self.students_names = []
        self.number_students = 0
        self.name_export = ""
        self.count_tasks = ""
        self.name_test = ""
        self.generate_file_names = []
        self.generate_branch_names = []
        self.read_student_tasks_info(args[0],args[1],args[2])
        self.branch_help = 0
        self.file_help = 0


    def read_student_tasks_info(self,student_id,task_id,test_name):
        """Nacitaju sa uz vygenerovane informacie """

        self.set_student_id(student_id)
        self.set_task_id(task_id)
        self.set_name_test(test_name)

        self.read_from_test_info() 

        self.generate_file_names = self.make_names_array()
        self.generate_branch_names = self.make_names_array() 
        
        self.read_exist_names()   

        
    def read_from_test_info(self):
        """Nacitaju sa informacie o teste """

        path_info = self.get_system_path()+"tests_files/"+self.get_name_test()+"/test_info.csv"

        students_names = []
        if Path(path_info).exists():
            with open(path_info,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                num = 0
                for row in reader:
                    if row['Name'] == "all.students":                    
                        self.set_name_export(row['Name Export File'])
                        self.set_count_tasks(row['Count Tasks'])              
                    else:
                        students_names.append(row['Name'])
                        num += 1

                self.set_students_names(students_names)
                self.set_number_students(num)
        else:
            print("File with test info not exist.")

    def select_branch_name(self):
        """Vyberie sa ci uz vybrane meno alebo sa vybera nove meno pre vetvu """
        path = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()
                    [self.get_student_id()]+"/"+"select_branch.csv")

        if Path(path).exists():
            return self.select_exist_branch_name()
        else:
            return self.select_new_branch_name()
        

    def select_new_branch_name(self):
        """Vyberie sa meno z pripravenych mien pre vetvy """
        
        if Path(self.get_system_path()+"names/names.txt").exists():
            with open(self.get_system_path()+"names/names.txt","r") as file:
                branch_name_list = file.readline()
        else:
            print("File with names not exist.")
        
        is_in_there = True

        while is_in_there == True:
            act_name_int = random.randint(1, 30)
            act_name = branch_name_list.split(',')[act_name_int-1]
            is_in_there =  self.check_exist_in_array(act_name,self.get_generate_branch_names())

        self.write_name_to_backup(act_name,"branch")
        self.write_name_for_conflicts(act_name)

        self.get_generate_branch_names()[self.get_task_id()].append(act_name)
        return act_name


    def select_exist_branch_name(self):
        """Vyberie sa meno suboru """

        name = self.get_generate_branch_names()[self.get_task_id()][self.branch_help]

        self.branch_help += 1
        return name


    def select_file_name(self):
        """Vyberie sa ci uz vybrane meno alebo sa vybera nove meno pre subor """

        path = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()
                    [self.get_student_id()]+"/"+"select_file.csv")

        if Path(path).exists():
            return self.select_exist_file_name()
        else:
            return self.select_new_file_name()

    def select_new_file_name(self):
        """Vyberie sa meno suboru z pripravenych suborov """

        is_in_there = True
                    
        while is_in_there == True:
            act_name = random.choice(os.listdir(self.get_system_path()+"names/files"))
            full_name = random.choice(os.listdir(self.get_system_path()+"names/files/"+act_name))
            full_name = full_name.split(".")[2]
            act_name = act_name +"."+full_name
            
            is_in_there =  self.check_exist_in_array(act_name,self.get_generate_file_names())

        self.write_name_to_backup(act_name,"file")
        
        self.get_generate_file_names()[self.get_task_id()].append(act_name)
        return act_name

    def select_exist_file_name(self):
        """Vyberie sa meno suboru, ktore uz bolo vybrane """
        name = self.get_generate_file_names()[self.get_task_id()][self.file_help]

        self.file_help += 1
        return name

    def select_text_for_file(self,file_name):
        """Vyberie sa text do ulohy pre vybrany subor """

        split_name = file_name.split(".")
        path = self.get_system_path()+"names/files/"+split_name[0]+"/"+split_name[0]+".text."+split_name[1]

        with open(path) as file:  
            data = file.read() 

        return data.replace("\n","")

    def check_exist_in_array(self,act_name,array):
        """Kontrola ci uz existuje meno ktore sa vygenerovalo """
      
        is_in_there = False
        for tasks_names in array:
            for name in tasks_names:
                if name == act_name:                    
                    is_in_there = True
        return is_in_there

    def write_name_to_backup(self,name,type_name):
        """Zapis mena do zalohy """

        path_info = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"
                +self.get_students_names()[self.get_student_id()]+"/"+"task-"+str(self.get_task_id()+1)+".csv")

        if Path(path_info).exists():
            is_write_header = True
        else:
            is_write_header = False

        os.makedirs(os.path.dirname(path_info),exist_ok=True)
        with open(path_info,"a",encoding = "ISO-8859-1") as csv_file:
            field_names = ['type_name','name']

            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            if is_write_header == False:
                writer.writeheader()
                
            writer.writerow({'type_name':type_name,'name':name})

     
    def write_name_for_conflicts(self,name):
        """Zapisu sa mena do suboru pre konflikty """ 
 
        path = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"
                +self.get_students_names()[self.get_student_id()]+"/conflict_info.csv")

        if Path(path).exists():
            is_write_header = True
        else:
            is_write_header = False

        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"a",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Name','Is_Use','Task_Id']

            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            if is_write_header == False:
                writer.writeheader()

            writer.writerow({'Name':name,'Is_Use':'No','Task_Id':self.get_task_id()})


    def make_names_array(self):
        """Vytvori pole kde sa budu ukladat mena suborov a vetiev """

        x = int(self.get_count_tasks())
        y = 0

        two_d_array = []
        for i in range(x):
            temp = []
            for j in range(y):
                temp.append('')
            two_d_array.append(temp)
        return two_d_array


    def read_exist_names(self):
        """Nacitaju sa uz existujuce mena ulohy """

        for act_task_id in range(int(self.get_count_tasks())):
            path = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()
                    [self.get_student_id()]+"/"+"task-"+str(act_task_id+1)+".csv")
            if Path(path).exists():
                self.read_concrete_task_names(path,act_task_id)


    def read_concrete_task_names(self,path,act_task_id):
        """Nacitaju sa existujuce mena pre konkretnu ulohu """
 
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                for row in reader:
                    for head in header:
                        if row['type_name'].find("branch") != -1 and head == 'name' and row[head] != "":
                            self.get_generate_branch_names()[act_task_id].append(row['name'])
                        elif row['type_name'].find("file") != -1 and head == 'name' and row[head] != "":
                            self.get_generate_file_names()[act_task_id].append(row['name'])
        else:
            print("File with task names not exist.")

 
    def make_branch_to_student_project_from_branch(self,branch_name,from_branch_name):
        """Vytvorenie vetvy v repozitary pre studenta """

        type = "student"
        student_name = self.get_students_names()[self.get_student_id()]

        path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name

        repo = git.Repo(path)
        repo.git.checkout(from_branch_name)
        repo.git.checkout('HEAD', b=branch_name)
        os.system("touch "+path+"/branch-"+branch_name+".txt")
        self.add_commit_and_push(repo,branch_name)
        repo.git.checkout("master")


    def make_branch_to_correct_solution_from_branch(self,new_branch_name,from_branch_name):
        """Vytvorenie vetvy do repozitara so spravnym riesenim """

        type = "evaluate"
        student_name = self.get_students_names()[self.get_student_id()]

        path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name
        
        repo_student = git.Repo(self.get_system_path()+"bot/"+self.get_name_test()+"/student/"+student_name)
        repo = git.Repo(path)
        repo.git.checkout(from_branch_name)
        repo.git.checkout('HEAD', b=new_branch_name)
        all_branches = repo_student.git.branch('-r') + '\n'
        if all_branches.find(new_branch_name+'\n') != -1:
            os.system("touch "+path+"/branch-"+new_branch_name+".txt")
            self.add_commit_and_push(repo,new_branch_name)
        repo.git.checkout("master")


    def make_empty_file_to_correct_solution_branch(self,branch_name,file_name):
        """Vytvorenie prazdneho suboru do vetvy v repozitary pre spravne riesenie """

        type = "evaluate"
        self.make_empty_file(type,file_name,branch_name)


    def make_empty_file_to_student_branch(self,branch_name,file_name):
        """Vytvorenie prazdneho suboru do projektu studenta """

        student_name = self.get_students_names()[self.get_student_id()]

        type = "student"
        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+student_name+"/actual_branch.csv"

        if Path(path).exists() == False or self.is_equal_branch_with_actual_branch(branch_name,student_name) == True:
            self.make_empty_file(type,file_name,branch_name)
            if self.is_equal_branch_with_actual_branch(branch_name,student_name):
                self.change_branch_to_print_conflict(branch_name,student_name) 

 
    def make_empty_file(self,type,file_name,branch_name):
        """Vytvori sa prazdny subor podla parametrov """            

        student_name = self.get_students_names()[self.get_student_id()]
        path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name
        repo = git.Repo(path)
        repo.git.checkout(branch_name)
        os.system("touch "+path+"/"+file_name)
        self.add_commit_and_push(repo,branch_name)
        repo.git.checkout("master")


    def make_file_to_student_branch(self,branch_name,file_name):
        """Vytvori sa neprazdny subor do projektu studenta """

        type = "student"
        student_name = self.get_students_names()[self.get_student_id()]
        path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name

        path_conflict = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+student_name+"/actual_branch.csv"

        if Path(path_conflict).exists() == False or self.is_equal_branch_with_actual_branch(branch_name,student_name) == True:
        
            repo = git.Repo(path)
            repo.git.checkout(branch_name)

            split_name = file_name.split(".")
            path_from_copy = self.get_system_path()+"names/files/"+split_name[0]+"/"+split_name[0]+".init."+split_name[1]
            shutil.copy2(path_from_copy,path+"/"+file_name)

            self.add_commit_and_push(repo,branch_name)
            repo.git.checkout("master")

            if self.is_equal_branch_with_actual_branch(branch_name,student_name):
                self.change_branch_to_print_conflict(branch_name,student_name)


    def make_file_to_correct_solution_branch(self,branch_name,file_name):
        """Vytvory sa subor z korektnym obsahom pre spravne riesenie """
        
        type = "evaluate"
        student_name = self.get_students_names()[self.get_student_id()]
        path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name
        
        repo = git.Repo(path)
        repo.git.checkout(branch_name)

        split_name = file_name.split(".")
        path_from_copy = self.get_system_path()+"names/files/"+split_name[0]+"/"+split_name[0]+".correct."+split_name[1]
        
        shutil.copy2(path_from_copy,path+"/"+file_name)

        self.add_commit_and_push(repo,branch_name)
        repo.git.checkout("master")
        

    def modify_file_in_student_branch(self,branch_name,file_name):
        """Zmeni sa obsah suboru """
        
        student_name = self.get_students_names()[self.get_student_id()]
        path_conflict = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+student_name+"/actual_branch.csv"

        if Path(path_conflict).exists() == False or self.is_equal_branch_with_actual_branch(branch_name,student_name) == True:

            type = "student"
            
            path = self.get_system_path()+"bot/"+self.get_name_test()+"/"+type+"/"+student_name
        
            repo = git.Repo(path)
            repo.git.checkout(branch_name)
        
            os.system("rm -rf "+path+"/"+file_name)

            split_name = file_name.split(".")
            path_from_copy = self.get_system_path()+"names/files/"+split_name[0]+"/"+split_name[0]+".change."+split_name[1]
            shutil.copy2(path_from_copy,path+"/"+file_name)

            self.add_commit_and_push(repo,branch_name)
            repo.git.checkout("master") 
            if self.is_equal_branch_with_actual_branch(branch_name,student_name):
                self.change_branch_to_print_conflict(branch_name,student_name)      


    def add_commit_and_push(self,repo,branch):
        """Vykonaju sa prikazi add commit a push """

        repo.git.add( '.' )
    
        st = repo.git.commit( m='commit branch')
   
        push_st = repo.git.push("origin", branch)

    def is_equal_branch_with_actual_branch(self,branch,student_name):
        """Porovnanie vetvy z aktualnou vetvou, ktora bola zapisana do vzdialeneho repozitara """

        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+student_name+"/actual_branch.csv"
        actual_branch = ""

        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')

                for row in reader:
                    if row['Branch'] != "":
                        actual_branch = row['Branch']
    
        if actual_branch == branch:
            return True
        else:
            return False

    def change_branch_to_print_conflict(self,branch_name,student_name):
        """Povoli sa vypis konfliktu """

        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+student_name+"/actual_branch.csv"
        
        if Path(path).exists():

            with open(path,"w",encoding = "ISO-8859-1") as csv_file:
                field_names = ['Branch','Print']
                writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
                writer.writeheader()

                writer.writerow({ 'Branch':branch_name, 'Print' : 'Yes' })
        else:
            print("File with actual branch csv not exist")


    def compare_student_and_correct_solution_branches(self,student_branch_name,correct_branch_name):
        """Porovnanie studentovej vetvy z spravnym riesenim """

        self.pull_branch(student_branch_name)
        return self.compare_branches(student_branch_name,correct_branch_name)


    def pull_branch(self,branch):
        """Stiahne sa zadana vetva so vzdialeneho repozitara """

        path = self.get_system_path()+"bot/"+self.get_name_test()+"/student/"+self.get_students_names()[self.get_student_id()]
        g = git.Git(path)
        repo = git.Repo(path)

        for remote in repo.remotes:
                remote.fetch()
        
        all_branches = g.branch('-r') + '\n'
       
        if all_branches.find(branch+'\n') != -1:
            repo.git.checkout(branch)
            
            g.pull('origin',branch)
        repo.git.checkout('master')


    def compare_branches(self,student_branch,correct_branch):
        """Porovna sa obsah vetiev """

        path_student = self.get_system_path()+"bot/"+self.get_name_test()+"/student/"+self.get_students_names()[self.get_student_id()]
        path_evaluate = self.get_system_path()+"bot/"+self.get_name_test()+"/evaluate/"+self.get_students_names()[self.get_student_id()]

        repo_student = git.Repo(path_student)
        repo_evaluate = git.Repo(path_evaluate)
        
        all_branches = repo_student.git.branch('-r') + '\n'
        if all_branches.find(student_branch+'\n') != -1:
            repo_student.git.checkout(student_branch)

        all_branches = repo_evaluate.git.branch('-r') + '\n'
        if all_branches.find(correct_branch+'\n') != -1:
            repo_evaluate.git.checkout(correct_branch)

        dest,dest_correct = self.copy_directory_to_compare() 
        is_same = self.same_folders(filecmp.dircmp(dest, dest_correct))

        repo_student.git.checkout('master')
        repo_evaluate.git.checkout('master')
        os.system("sudo rm -rf "+self.get_system_path()+"bot/compare")

        return is_same


    def same_folders(self,compared):
        """Porovnaju sa obsahy adresarov porovnavanych vetiev """

        if (compared.left_only or compared.right_only or compared.diff_files 
            or compared.funny_files):
            return False
        for subdir in compared.common_dirs:
            if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
                return False
        return True


    def copy_directory_to_compare(self):
        """Pomocna funkcia nam pripravy adresare na skopirovanie, ktore sa budu porovnavat """

        os.makedirs(os.path.dirname(self.get_system_path()+"bot/compare/"+self.get_students_names()[self.get_student_id()]+"/"),exist_ok=True)
        os.makedirs(os.path.dirname(self.get_system_path()+"bot/compare/"+self.get_students_names()[self.get_student_id()]+"-correct"+"/"),exist_ok=True)

        src=self.get_system_path()+"bot/"+self.get_name_test()+"/student/"+self.get_students_names()[self.get_student_id()]+"/"
        dest=self.get_system_path()+"bot/compare/"+self.get_students_names()[self.get_student_id()]
        self.copy_to_compare(src,dest)

        src_correct=self.get_system_path()+"bot/"+self.get_name_test()+"/evaluate/"+self.get_students_names()[self.get_student_id()]+"/"
        dest_correct=self.get_system_path()+"bot/compare/"+self.get_students_names()[self.get_student_id()]+"-correct"
        self.copy_to_compare(src_correct,dest_correct)

        self.files_without_whitespace(dest)
        self.files_without_whitespace(dest_correct)
        return (dest,dest_correct)

    def copy_to_compare(self,src,dest):
        """Pomocna metoda na skopirovanie suborov v adresary, ktore sa budu porovnavat """

        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

    def files_without_whitespace(self,path):
        """Pomocna metoda, ktora odstrani biele znaky zo suborov """
        
        files = os.listdir(path)
        for file_name in files:
            file_cm = ""
            with open(path+"/"+file_name,"r") as file:
                for line in file:
                    file_cm += line.replace(" ","").replace("\n","")
            with open(path+"/"+file_name,"w") as file:
                file.write(file_cm)


    def get_number_students(self):
        return self.number_students

    def set_number_students(self,number_students):
        self.number_students = number_students

    def get_students_names(self):
        return self.students_names

    def set_students_names(self,students_names):
        self.students_names = students_names

    def get_count_tasks(self):
        return self.count_tasks

    def set_count_tasks(self,count_tasks):
        self.count_tasks = count_tasks

    def get_name_export(self):
        return self.name_export

    def set_name_export(self,name_export):
        self.name_export = name_export

    def get_name_test(self):
        return self.name_test

    def set_name_test(self,name_test):
        self.name_test = name_test

    def get_generate_file_names(self):
        return self.generate_file_names

    def get_generate_branch_names(self):
        return self.generate_branch_names

    def get_student_id(self):
        return self.student_id

    def set_student_id(self,student_id):
        self.student_id = student_id

    def get_task_id(self):
        return self.task_id
    
    def set_task_id(self,task_id):
        self.task_id = task_id

    def get_system_path(self):
        path_to_system = os.path.realpath(__file__)
        return self.parser.check_something(path_to_system,"","gitmaker.py")