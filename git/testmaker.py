"""Test_maker modul

Tento modul nam zabezpecuje vytvorenie testu a pripravu pre vytvorenie uloh testu
pomocou informacii, ktore prebera z modulu parser.
"""

from parser import Parser
import csv
import os
import crypt
import random
import re
import shutil
import sys
from pathlib import Path
import git
import importlib


class TestMaker:

    def __init__(self):
        self.students_names  = []
        self.test_password = ""
        self.test_time = ""
        self.name_export = ""
        self.count_tasks = ""
        self.name_test = "defaultName"
        self.number_students = 0
        self.student_id = 0
        self.task_id = 0
        
    
    def read_test_info(self,path_info):
        """Nacita z suboru csv zakladne info o vytvaranom teste. """
 
        parser = Parser("")
        students_names = []
        if Path(path_info).exists():
            with open(path_info,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                num = 0
                for row in reader:
                    if row['Name'] == "all.students":                    
                        self.set_test_password(row['Password'])
                        self.set_test_time(row['Time'])
                        self.set_name_export(row['Name Export File'])
                        self.set_count_tasks(row['Count Tasks'])
                        self.set_name_test(row['Name Test'])
               
                    else:
                        students_names.append(row['Name'])
                        num += 1

                self.set_students_names(students_names)
                self.set_number_students(num)
        else:
            print("File with test info not exist.")


    def generate_tasks(self,path_info):
        """Vygeneruju ulohy pre vsetkych studentov. """

        self.remove_enviroment()
        generate_tasks = self.two_d_array_string(int(self.get_number_students()),int(self.get_count_tasks()))

        if int(self.get_count_tasks())  <= int(self.get_max_num_tasks()):
            for i in range(int(self.get_number_students())):              
                generate_tasks[i] = self.generate_tasks_for_student(int(self.get_count_tasks()))
            
            self.set_generate_tasks(generate_tasks)
            self.write_generate_tasks(path_info)
  
            return self.get_generate_tasks()
        else:
            return "error"


    def generate_tasks_for_student(self,count_tasks):
        """Vygeneruju sa ulohy z mnoziny uloh """
        
        path = self.get_system_path()+"define_tasks"
        tasks_list = []
        
        for i in range(count_tasks):
            file_name = self.generate_name_for_task(path,tasks_list)
            tasks_list.append(file_name)
        
        return tasks_list

    def generate_name_for_task(self,path,tasks_names):
        """Vygeneruje sa meno konkretnej ulohy """
        
        is_selected = True
        while is_selected == True:
            is_selected = False
            selected_name = random.choice(os.listdir(path))
            if selected_name.endswith('.py') == False:
                is_selected = True
            for name in tasks_names:
                if name == selected_name:
                    is_selected = True
        
        return selected_name
        

    def write_generate_tasks(self,path_info):
        """Zapise sa nova verzia csv z ulohami """

        os.makedirs(os.path.dirname(path_info),exist_ok=True)
        with open(path_info,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Name','Password','Time','Name Export File', 'Count Tasks', 'Name Test','Tasks Index']
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            writer.writerow({'Name':'all.students','Password':self.get_test_password(),'Time':self.get_test_time(),
                            'Name Export File':self.get_name_export(),'Count Tasks':self.get_count_tasks(),
                            'Name Test':self.get_name_test()})
            i = 0
            for student_name in self.get_students_names():
                if student_name != "":
                    writer.writerow({ 'Name':student_name,'Tasks Index' : self.get_generate_tasks()[i] })
                    i += 1


    def create_tasks(self,parser):
        """Spusti sa vytvaranie uloh pre jednotlivych studentov """
                 
        for i in range(self.get_number_students()):
            self.set_student_id(i)
            path = "/home/"+self.get_students_names()[i]
            with open(path+"/zadanie","w") as f:
                f.write("\n-------------\nGit Trenazer\n-------------\n\n")
                                       
            for j in range(int(self.get_count_tasks())):
                self.set_task_id(j)
                self.create_task_for_student(parser)

            self.prepare_for_changes(i)
        

    def create_task_for_student(self,parser):
        """Spusti sa vytvaranie jednotlivej ulohy """
        
        name_module = self.get_generate_tasks()[self.get_student_id()][self.get_task_id()]
        name_module = self.check_something(name_module,"",".py")
        TASK_NAME = "define_tasks." + name_module
        tasks_module = importlib.import_module(TASK_NAME,".")
        task = tasks_module.Tasks(self.get_student_id(),self.get_task_id(),self.get_name_test())
        task_text = task.define_task_text()
        task.create_student_start_repository()
        task.create_correct_solution_project()
        self.write_task_text(task_text)

    def change_students_repository(self,student_name,task_id,test_name):
        """Spusti sa vykonavanie zmeny studentovho repozitara po tom ako sa pokusi zapisat do repozitara (generovanie konfliktov) """

        path = self.get_system_path()+"tests_files/"+test_name+"/test_info.csv"
        self.read_test_info(path)
        student_id = self.get_student_id_from_name(student_name)
        self.set_task_id(int(task_id))
        self.set_student_id(student_id)
        self.change_repository()

    def get_student_id_from_name(self,student_name):
        """Zisti sa id studenta v teste z jeho mena """
        student_id = -1
        for i in range(int(self.get_number_students())):
            if self.get_students_names()[i] == student_name:
                student_id = i

        return student_id                


    def change_repository(self):
        """Spusti sa zmena konkretnej ulohy """

        name_module = self.read_tasks_name()
        name_module = self.check_something(name_module,"",".py")
        TASK_NAME = "define_tasks." + name_module
        tasks_module = importlib.import_module(TASK_NAME,".")
        task = tasks_module.Tasks(self.get_student_id(),self.get_task_id(),self.get_name_test())
        task.change_repository_before_first_push()

    def write_task_text(self,text):
        """Zapise sa znenie ulohy do suboru pre studenta """
 
        path = "/home/"+self.get_students_names()[self.get_student_id()]
        with open(path+"/zadanie","a") as f:
            f.write(str(self.get_task_id()+1)+". "+text+"\n\n")


    def read_tasks_name(self):
        """Nacita nazvy uloh """

        ulohy = []
        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/test_info.csv"

        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames

                for row in reader:
                    for head in header:
                        if row['Name'] == self.get_students_names()[self.get_student_id()]:
                            ulohy = row['Tasks Index']
        else:
            print("File with test info not exist.")
        ulohy = ulohy.replace("[", "").replace("]","").replace("\'","").replace(" ","")
        ulohy = ulohy.split(',')
        return ulohy[self.get_task_id()]

    
    def check_something(self,line,before,behind):
        """Pomocna funkcia vrati nieco co sa nachadza medzi zadanimi hodnotami v retazci """

        some_string = re.findall(r''+before+'(.*?)'+behind,line)
        some_string = ''.join(some_string)
        return some_string


    def create_users(self):
        """Vytvoria sa pouzivatelia pre studentov """

        encrypt_password = crypt.crypt(self.get_test_password(),"22")
        
        for i in range(self.get_number_students()):

            os.system("sudo useradd -m -s /bin/bash -p"+ encrypt_password + " " + self.get_students_names()[i])
            os.system("sudo groupadd group_"+self.get_students_names()[i])
            os.system("sudo usermod -a -G group_"+self.get_students_names()[i]+" "+self.get_students_names()[i])
            os.chmod("/home/"+self.get_students_names()[i],0o700)

            os.system("sudo usermod -a -G students "+self.get_students_names()[i])
        
            
    def create_projects_for_test(self):
        """Vytvoria sa git projekty """ 

        for i in range(self.get_number_students()):
            stud_name = self.get_students_names()[i]

            git.Repo.init("/home/"+stud_name+"/student/project_"+stud_name+".git", bare=True)
            os.system("sudo chgrp -R group_"+stud_name+" /home/"+stud_name+"/student/project_"+stud_name+".git/.")
            os.system("sudo chmod -R 777 /home/"+stud_name+"/student/project_"+stud_name+".git/.")
            self.initialize_commit(self.get_students_names()[i],"student")

            git.Repo.init("/home/"+stud_name+"/evaluate/project_"+stud_name+".git", bare=True)
            os.system("sudo chgrp -R group_"+stud_name+" /home/"+stud_name+"/evaluate/project_"+stud_name+".git/.")
            os.system("sudo chmod -R 000 /home/"+stud_name+"/evaluate/project_"+stud_name+".git/.")
            self.initialize_commit(self.get_students_names()[i],"evaluate")
            
        self.actual_test(self.get_name_test())
      

    def initialize_commit(self,name,type):
        """Prvy commmit po vytvoreni projektu """
        
        name_test = self.get_name_test()

        repo = git.Repo.clone_from("/home/"+name+"/"+type+"/project_"+name+".git", self.get_system_path()+"bot/"+name_test+"/"+type+"/"+name)
        with repo.config_writer() as wr:
            wr.set_value('user', 'email', "peter@tuke.sk")
            wr.set_value('user', 'name', "peter")
        
        os.system("sudo chmod -R 777 "+self.get_system_path()+"bot/"+name_test+"/"+type+"/"+name+"/.")
        os.system("touch "+self.get_system_path()+"bot/"+name_test+"/"+type+"/"+name+"/init.txt")
        
        repo.git.add( '.' )
        repo.git.commit( m='my commit message')

        repo.git.push("origin", "master")

        for remote in repo.remotes:
            remote.fetch()


    def prepare_for_changes(self,student_id):
        """Pripravi sa vsetko potrebne pre generovanie konfliktov. """

        system_dir = self.get_system_path()+"update.py"
        stud_name = self.get_students_names()[student_id]
        student_project = ("/home/"+self.get_students_names()[student_id]+"/student/project_"
                            +self.get_students_names()[student_id]+".git/hooks/update")
        os.system("sudo ln -s "+system_dir+" "+student_project)

        os.system("sudo chmod -R 777 /home/"+stud_name+"/student/project_"+stud_name+".git/.")
        os.system("sudo touch "+self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()
                    [student_id]+"/"+"select_file.csv")
        os.system("sudo touch "+self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()
                    [student_id]+"/"+"select_branch.csv")

        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()[student_id]
        os.system("sudo chmod -R 777 "+path+"/.")

        os.system("sudo chmod -R 777 "+self.get_system_path()+"bot/"+self.get_name_test()+"/student/"+self.get_students_names()[student_id]+"/.")


    def actual_test(self,name_test):
        """Nastavi sa aktualne vykonavany test. """

        path = self.get_system_path()+"tests_files/actual_test.csv"
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Test_Name']
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            writer.writerow({'Test_Name':name_test})


    def remove_users(self,name):
        """Vymazu sa pouzivatelia pre studentov. """

        path = self.get_system_path()+"tests_files/"+name+"/test_info.csv"
        self.read_test_info(path)

        for i in range(self.get_number_students()):
            os.system("sudo groupdel group_"+self.get_students_names()[i])
            os.system("sudo userdel -r "+self.get_students_names()[i])
            os.system("sudo rm -rf /home/"+self.get_students_names()[i])

        os.system("sudo rm -rf bot/"+name)

    def remove_only_student_enviroment(self,name_test):
        """Spusti sa vymazanie studentovych suborov a suborov potrebnych pre vykonanie testu. """
        
        path = self.get_system_path()+"tests_files/"+name_test+"/test_info.csv"
        self.read_test_info(path)

        for i in range(self.get_number_students()): 
            if self.exist_user(self.get_students_names()[i]) == True:
                self.remove_enviroment_student("/home/"+self.get_students_names()[i]+"/")
                self.remove_enviroment_student(self.get_system_path()+"bot/"+name_test+"/")
                
            else:
                print("> User "+self.get_students_names()[i]+" not exist.")

    def remove_backup_files(self,name_test):
        """Spusti sa vymazanie suborov pre zalohu. """

        path = self.get_system_path()+"tests_files/"+name_test+"/test_info.csv"
        self.read_test_info(path)
        os.system("sudo rm -rf "+self.get_system_path()+"bot/"+name_test)
        for i in range(self.get_number_students()):         
            self.remove_enviroment_student(self.get_system_path()+"tests_files/"+name_test+"/")
        

    def two_d_array_string(self,x,y):
        """Vytvory sa dvojrozmerne pole """

        two_d_array = []
        for i in range(x):
            temp = []
            for j in range(y):
                temp.append('')
            two_d_array.append(temp)
        return two_d_array


    def remove_enviroment(self):
        """Spusti vymazanie suborov, ktore sa nachadzaju v domovskych adresaroch studentov a ulozene kopie pre kontrolu """

        for i in range(self.get_number_students()):
            if self.exist_user(self.get_students_names()[i]) == True:
                self.remove_enviroment_student("/home/"+self.get_students_names()[i]+"/")
                self.remove_enviroment_student(self.get_system_path()+"tests_files/"+self.get_name_test()+"/")
            else:
                print("> User "+self.get_students_names()[i]+" not exist.")
       

    def remove_enviroment_student(self,folder):
        """Vymazu sa subory zo zadaneho adresara """
            
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)  


    def exist_user(self,user):
        """Zisti sa ci existuje domovsky adresar studenta """

        path = ("/home/"+user)
        if os.path.isdir(path) == True:
            return True
        else:
            return False   


    def get_max_num_tasks(self):
        """Prehladaju sa vsetky subory zo zadaniami uloh a podla toho sa urci ich pocet """

        dir = self.get_system_path()+"define_tasks"
        numTasks = len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
        return numTasks


    def get_students_names(self):
        return self.students_names

    def set_students_names(self,students_names):
        self.students_names = students_names
                    
    def get_test_password(self):
        return self.test_password

    def set_test_password(self,test_password):
        self.test_password = test_password   

    def get_test_time(self):
        return self.test_time

    def set_test_time(self,test_time):
        self.test_time = test_time                 
                
    def get_name_export(self):
        return self.name_export

    def set_name_export(self,name_export):
        self.name_export = name_export

    def get_count_tasks(self):
        return self.count_tasks

    def set_count_tasks(self,count_tasks):
        self.count_tasks = count_tasks
        
    def get_name_test(self):
        return self.name_test

    def set_name_test(self,name_test):
        self.name_test = name_test

    def get_number_students(self):
        return self.number_students

    def set_number_students(self,number_students):
        self.number_students = number_students

    def get_generate_tasks(self):
        return self.generate_tasks
    
    def set_generate_tasks(self,generate_tasks):
        self.generate_tasks = generate_tasks

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
        return self.check_something(path_to_system,"","testmaker.py")