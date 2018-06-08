"""Test_maker modul

Tento modul nam zabezpecuje vytvorenie testu a jednotlivych uloh testu
pomocou informacii, ktore prebera z modulu parser.
"""
from parser import Parser
import csv
import os
import crypt
import random
import subprocess
import re
import shutil
import linecache
import sys
from pathlib import Path

class TestMaker:


    def __init__(self):
        self.students_names  = []
        self.test_password = ""
        self.test_time = ""
        self.name_export = ""
        self.count_tasks = ""
        self.name_test = "defaultName"
        self.number_students = 0
        self.array_for_action = []
        self.generate_file_names = []
        self.generate_path_names = []
        self.generate_directory_names = []
        self.generate_rights_names = []
        self.student_id = 0
        self.task_id = 0
        
    
    def read_test_info(self,path_info):
        """Nacita z suboru csv zakladne info o vytvaranom teste """

        parser = Parser("")
        students_names = parser.make_string_array(25)
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
                        students_names[num] = row['Name']
                        num += 1

                self.set_students_names(students_names)
                self.set_number_students(num)
        else:
            print("File with test info not exist.")


    def generate_tasks(self,path_info):
        """Vygeneruju sa cisla(indexi) uloh pre vsetkych studentov """
        
        self.remove_enviroment()
        generate_tasks = self.two_d_array_int(int(self.get_number_students()),int(self.get_count_tasks()))

        if int(self.get_count_tasks())  <= int(self.get_max_num_tasks()):
            for i in range(int(self.get_number_students())):
                tasks_list = random.sample(range(1,(int(self.get_max_num_tasks()+1))),int(self.get_count_tasks()))
                generate_tasks[i] = tasks_list
            
            self.set_generate_tasks(generate_tasks)
            self.write_generate_tasks(path_info)
            return self.get_generate_tasks()
        else:
            return "error"
        

    def write_generate_tasks(self,path_info):
        """Zapise sa nova verzia csv z indexami uloh """
        
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

        self.generate_file_names = self.make_names_array()
        self.generate_path_names = self.make_names_array()
        self.generate_directory_names = self.make_names_array()
        self.generate_rights_names = self.make_names_array()  
                      

        for i in range(self.get_number_students()):
            self.set_student_id(i)
            path = "/home/"+self.get_students_names()[i]
            
            with open(path+"/zadanie","w") as f:
                f.write("\n-------------\nUnix Trenazer\n-------------\n\n")
                         
                
            for j in range(int(self.get_count_tasks())):
                self.set_task_id(j)
                self.create_task_for_student(parser)
                self.create_student_wording_file(parser,"/home/"+self.get_students_names()[i])
        
       

    def make_names_array(self):
        """Vytvori pole kde sa budu ukladat mena suborov, adresarov, pristupovych prav """

        x = int(self.get_number_students())
        y = int(self.get_count_tasks())
        z = 0

        three_d_array = []
        for i in range(x):
            temp = []
            for j in range(y):
                temp2 = []
                for k in range(z):
                    temp2.append(' ')
                temp.append(temp2)
            three_d_array.append(temp)
        return three_d_array
        

    def create_task_for_student(self,parser):
        """Spusti sa vytvaranie jednotlivej ulohy """
        
        help = []
        self.set_array_for_action(help)
        
        task_n = int(self.get_generate_tasks()[self.get_student_id()][self.get_task_id()])       
        name_task_file = self.get_system_path()+"tasks/task-"+str(task_n)+".txt"         
     
        parser.parse(name_task_file)
        parser.write_create_info(self.get_student_id(),"create_info-"+str(self.get_task_id()+1)+".csv")
        parser.write_evaluate_info(self.get_student_id(),"evaluate_info-"+str(self.get_task_id()+1)+".csv")
        self.read_parse_task("tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]
                            +"/create_info-"+str(self.get_task_id()+1)+".csv")
        self.task_creator()
        self.rewrite_evaluate_info("evaluate_info-"+str(self.get_task_id()+1)+".csv",parser)


    def rewrite_evaluate_info(self,name_file,parser):
        """Prepise sa csv subor pre vyhodnotenie, doplnia sa mena suborov, adresarov, pouzivatelske prava """

        path_info = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+str(self.get_students_names()[self.get_student_id()])
                    +"/"+name_file)
        path_info_2 = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+str(self.get_students_names()[self.get_student_id()])
                    +"/create_info-"+str(self.get_task_id()+1)+".csv")

        os.makedirs(os.path.dirname(path_info),exist_ok=True)
        if Path(path_info_2).exists():
            with open(path_info_2,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                for row in reader:
                    if row['text']!="":
                        text = row['text']
        else:
            print("File with create info not exist.")

        with open(path_info,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['files','name']
            field_names = parser.create_field_names(field_names,parser.get_array_for_evaluate())

            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
                    
            for riadok in parser.get_array_for_evaluate():
                helpArray = []
                for action_name in riadok:
                    if type(action_name) is str:
                        name = action_name
                    elif type(action_name) is list:
                        writer.writerow({'files':action_name[0],name:action_name[1]})
    
            count_file = self.number_elements(text,"file-")
            count_path = self.number_elements(text,"path-")
            count_directory = self.number_elements(text,"directory-")
            count_rights = self.number_elements(text,"rights-")
            
            for i in range(count_path):
                writer.writerow({'files':'path-'+str(i+1),'name':self.get_generate_path_names()
                                [self.get_student_id()][self.get_task_id()][i]})
                
            for i in range(count_file):
                writer.writerow({'files':'file-'+str(i+1),'name':self.get_generate_file_names()
                                [self.get_student_id()][self.get_task_id()][i]}) 

            for i in range(count_directory):
                writer.writerow({'files':'directory-'+str(i+1),'name':self.get_generate_dir_names()
                                [self.get_student_id()][self.get_task_id()][i]})

            for i in range(count_rights):
                writer.writerow({'files':'rights-'+str(i+1),'name':self.get_generate_rights_names()
                                [self.get_student_id()][self.get_task_id()][i]})

            
    def read_parse_task(self,path):
        """Nacitaju sa z csv subora informacie o vytvoreni ulohy """
        path = self.get_system_path()+path
        array_for_read = []
        
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
            
                for row in reader: 
                    if row['files'] != "":
                        array_for_read.append(row['files'])
                    
                    for head in header:
                        if head != 'files' and head != 'text' and row[head] != "":
                            temp = []
                            temp.append(head)
                            temp.append(row[head])
                            array_for_read.append(temp)
        else:
            print("File with create info not exist.")
                       
        pocet,name_files = self.number_files_in_array(array_for_read)
        for i in range(pocet):
            first = True
            for prvok in array_for_read:              
                if type(prvok) is str: 
                    if prvok == name_files[i]:
                        if first == True:
                            self.get_array_for_action().append(prvok)
                            first = False
                    help_prvok = prvok
                if type(prvok) is list and help_prvok == name_files[i]:
                    temp = []
                    temp.append(prvok[0])
                    temp.append(prvok[1])
                    self.get_array_for_action().append(temp)
 
 
    def task_creator(self):
        """Spusti sa vytvorenie jednotlivych akcii pre vytvorenie ulohy """
        
        have_make=""
        max_level=""
        min_level=""
        level=""
        locate_in=""
        generate_rights = ""
        act_prvok=""
        command_to_use=""
        
        self.get_array_for_action().append("last")

        for prvok in self.get_array_for_action():
            
            if type(prvok) is str:
                if prvok != act_prvok and self.check_something(act_prvok,"","-") == "path" and first == False:
                    self.create_path(have_make,max_level,min_level,level)
                    
                elif prvok != act_prvok and self.check_something(act_prvok,"","-") == "file":
                    self.create_file(have_make,locate_in)

                elif prvok != act_prvok and self.check_something(act_prvok,"","-") == "directory":
                    self.create_directory(have_make,locate_in)   

                elif prvok != act_prvok and self.check_something(act_prvok,"","-") == "rights":
                    self.generate_rights(generate_rights)
                elif prvok != act_prvok and act_prvok == "command":                  
                    self.use_command(command_to_use)

                first = False
                act_prvok = prvok
                
            elif type(prvok) is list:
                if self.check_something(act_prvok,"","-") == "path":
                    if prvok[0] == "make":
                        have_make = prvok[1]
                    elif prvok[0] == "max_level":
                        max_level = prvok[1]
                    elif prvok[0] == "min_level":
                        min_level = prvok[1]
                    elif prvok[0] == "level":
                        level = prvok[1]
                    else:
                        print("error path")
                
                if self.check_something(act_prvok,"","-") == "file":
                    if prvok[0] == "make":
                        have_make = prvok[1]
                    elif prvok[0] == "locate_in":
                        locate_in = prvok[1]
                    else:
                        print("error file")

                if self.check_something(act_prvok,"","-") == "directory":
                    if prvok[0] == "make":
                        have_make = prvok[1]
                    elif prvok[0] == "locate_in":
                        locate_in = prvok[1]
                    else:
                        print("error dir")

                if self.check_something(act_prvok,"","-") == "rights":
                    if prvok[0] == "random_rights":
                        generate_rights = prvok[1]
                    else:
                        print("error generate rights")
    
                if act_prvok == "command":
                    if prvok[0] == "use":
                        command_to_use = prvok[1]
                    else:
                        print("error use command")
      
    
    def check_something(self,line,before,behind):
        """Pomocna funkcia vrati nieco co sa nachadza medzi zadanimi hodnotami v retazci """

        some_string = re.findall(r''+before+'(.*?)'+behind,line)
        some_string = ''.join(some_string)
        return some_string


    def create_path(self,have_make,max_level,min_level,level):
        """Vytvori sa cesta podla zadanych parametrov """

        name_path = ""
        if max_level != "":
            if min_level == "":
                set_min_level = 0
            else:
                set_min_level=int(min_level)
            set_max_level=int(max_level)
            name_path = self.generate_path_name(set_min_level,set_max_level)

        if level != "":
            set_level=int(level)
            name_path = self.generate_path_name(set_level,set_level)

        name_path = "/home/"+self.get_students_names()[self.get_student_id()]+"/"+name_path

        if have_make == "yes":
            self.make_path(name_path)


    def create_file(self,have_make,locate_in):
        """Vytvori sa subor podla zadanych parametrov """
      
        path = []
        path_help = 1
        path_name = "/home/"+self.get_students_names()[self.get_student_id()]+"/"
        path_name = ""
        for prvok in self.get_generate_path_names()[self.get_student_id()][self.get_task_id()]:
            if "path-"+str(path_help) == locate_in:
                path_name = self.get_generate_path_names()[self.get_student_id()][self.get_task_id()][path_help-1]
            path_help += 1
        path_name = "/home/"+self.get_students_names()[self.get_student_id()]+"/" + path_name
        file_name = self.generate_file_name()
        path_for_evaluate = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+(self.get_students_names()
                            [self.get_student_id()])+"/files/")

        os.makedirs(path_for_evaluate,exist_ok=True,mode=0o777)
        path_for_evaluate = path_for_evaluate +"/"+file_name

        if locate_in != "":
            path.append(path_name + file_name)
        else:
            path.append(file_name)
        path.append(path_for_evaluate)    

        if have_make == "yes":
            self.make_file_with_content(path)


    def create_directory(self,have_make,locate_in):
        """Vytvori sa adresar podla zadanych parametrov """

        path = ""
        path_help = 1
        path_name = ""

        for prvok in self.get_generate_path_names()[self.get_student_id()][self.get_task_id()]:
            if "path-"+str(path_help) == locate_in:
                path_name = (self.get_generate_path_names()[self.get_student_id()]
                            [self.get_task_id()][path_help-1])
            path_help += 1

        directory_name = self.generate_directory_name()
        path_name = "/home/"+self.get_students_names()[self.get_student_id()]+"/"+path_name
        if locate_in != "":
            path = (path_name + directory_name)
        else:
            path = ("/home/"+self.get_students_names()[self.get_student_id()]+"/"+directory_name)

        if have_make == "yes":
            self.make_path(path)
       
    def use_command(self,command):
        """Pouzije sa prikaz pri vytvarani ulohy """

        command = self.make_command_with_names(command)
        os.system(command)

    def make_command_with_names(self,command):
        """Prida mena suborov a ciest do prikazu """

        file_in_system = self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]+"/files/"
        number_file = self.number_elements(command,"file-")        
        number_path = self.number_elements(command,"path-")
        number_directory = self.number_elements(command,"directory-")
        number_absolute = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape("absolute"), command))       
 
        correct_command = command

        for i in range(number_file):
            correct_command = correct_command.replace("{file-"+str(i+1)+"}",
            str(self.get_generate_file_names()[self.get_student_id()][self.get_task_id()][i]))   
        for i in range(number_path):
            correct_command = correct_command.replace("{path-"+str(i+1)+"}",
            str(self.get_generate_path_names()[self.get_student_id()][self.get_task_id()][i]))
        for i in range(number_directory):
            correct_command = correct_command.replace("{directory-"+str(i+1)+"}",
            str(self.get_generate_dir_names()[self.get_student_id()][self.get_task_id()][i]))
        for i in range(number_absolute):
            correct_command = correct_command.replace("{absolute}","/home/"+self.get_students_names()[self.get_student_id()]+"/")
        if correct_command.find("{system}") != -1:
            correct_command = correct_command.replace("{system}",file_in_system)

        return correct_command

  
    def generate_rights(self,have_generate):
        """Vytvoria sa pouzivatelske prava """
  
        list = []
        for i in range (3):
            list.append(random.randint(1,7))

        if list[0] == 7 and list[1] == 7 and list[2] == 7:
            self.generate_rights(have_generate)
        self.get_generate_rights_names()[self.get_student_id()][self.get_task_id()].append(list)
   

    def make_file_with_content(self,path):
        """Vytvori sa nahodny obsah suboru """

        lines = []
        number_lines = random.randint(4, 10)
        for a in range(number_lines):
            lines.append(linecache.getline(self.get_system_path()+"data/sentences.txt",random.randint(1, 30)))
        
        for concrete_path in path:
            with open(concrete_path, "w") as f:
                f.write("a\n")
                for line in lines:
                    f.write(line)
                        
        os.chmod(path[0],mode=0o777)
        os.system("sudo chown "+self.get_students_names()[self.get_student_id()]+" "+path[0])


    def generate_directory_name(self):
        """Vygeneruju sa mena pre adresar """
        path = self.get_system_path()+"data/names.txt"
        if Path(path).exists():
            with open(path,"r") as file:
                file.readline()
                directory_name_list = file.readline()
        else:
            print("File with names not exist.")
        
        act_name_int = random.randint(1, 50)  
        act_name = directory_name_list.split(',')[act_name_int-1]
                    
        path_array = []
        for name in self.get_generate_path_names()[self.get_student_id()][self.get_task_id()]:
            path_array.append(name)

        for names in self.get_generate_dir_names()[self.get_student_id()]:
            for name in names:
                path_array.append(name)

        is_in_there = False
        for name in path_array:
            if name == act_name:
                is_in_there = True

            while is_in_there == True:
                is_in_there = False
                    
                act_name_int = random.randint(1, 50)
                act_name = directory_name_list.split(',')[act_name_int-1]
                    
                for name in path_array:
                    if name == act_name:
                        is_in_there = True
      
        self.get_generate_dir_names()[self.get_student_id()][self.get_task_id()].append(act_name)
        return act_name
                

    def generate_path_name(self,min_level,max_level):
        """Vygeneruju sa mena pre cestu """
        path_file = self.get_system_path()+"data/names.txt"
        if Path(path_file).exists():
            with open(path_file,"r") as file:
                file.readline()
                dir_name_list = file.readline()
        else:
            print("File with names not exist.")

        random_level = random.randint(min_level,max_level)
        path_array = []

        for i in range(random_level):
            path_array.append('')
 
        for i in range(random_level):
            actual_name_int = random.randint(1, 50)
            act_name = dir_name_list.split(',')[actual_name_int-1]
            
            is_in_there = False
          
            for name in path_array:
                if name == act_name:
                    is_in_there = True

                while is_in_there == True:
                    is_in_there = False
                    
                    actual_name_int = random.randint(1, 50)
                    act_name = dir_name_list.split(',')[actual_name_int-1]
                    
                    for name in path_array:
                        if name == act_name:
                            is_in_there = True
            path_array[i] = act_name
        path = ""
        for i in range(random_level):
            path=path+path_array[i]+"/"
         
        self.get_generate_path_names()[self.get_student_id()][self.get_task_id()].append(path)
        return path


    def generate_file_name(self):
        """Vygeneruje sa meno pre subor """
        path_file = self.get_system_path()+"data/names.txt"
        if Path(path_file).exists():
            with open(path_file,"r") as file:
                file_name_list = file.readline()
        else:
            print("File with names not exist.")

        act_name_int = random.randint(1, 50)
        act_name = file_name_list.split(',')[act_name_int-1]
        is_in_there = False
        for tasks_names in self.get_generate_file_names()[self.get_student_id()]:
            for name in tasks_names:
                if name == act_name:
                    is_in_there = True

        while is_in_there == True:
            is_in_there = False
            act_name_int = random.randint(1, 50)
            act_name = file_name_list.split(',')[act_name_int-1]
            for t_names in self.get_generate_file_names()[self.get_student_id()]:
                for name in t_names:
                    if name == act_name:
                        is_in_there = True

        self.get_generate_file_names()[self.get_student_id()][self.get_task_id()].append(act_name)
        return act_name


    def create_student_wording_file(self,parser,path):
        """Vytvori sa subor v ktorom sa bude nachadzat zadanie studenta """

        text = parser.get_task_text()
        
        count_file = self.number_elements(text,"file-")
        count_path = self.number_elements(text,"path-")
        count_directory = self.number_elements(text,"directory-")
        count_rights = self.number_elements(text,"rights-")
       
        for i in range(count_path):
            if (text.find("{path-"+str(i+1)+"}"))!=-1:
                text = text.replace("{path-"+str(i+1)+"}","/home/"+(self.get_students_names()
                                    [self.get_student_id()])+"/"+(self.get_generate_path_names()
                                    [self.get_student_id()][self.get_task_id()][i]))

        for i in range(count_file):
            if (text.find("{file-"+str(i+1)+"}"))!=-1:
                text = text.replace("{file-"+str(i+1)+"}",(self.get_generate_file_names()
                                    [self.get_student_id()][self.get_task_id()][i]))

        for i in range(count_directory):
            if (text.find("{directory-"+str(i+1)+"}"))!=-1:
                text = text.replace("{directory-"+str(i+1)+"}",(self.get_generate_dir_names()
                                    [self.get_student_id()][self.get_task_id()][i]))

        for i in range(count_rights):
            if (text.find("{rights-"+str(i+1)+"}"))!=-1:
                text_rights = self.make_text_rights(self.get_generate_rights_names()
                                                    [self.get_student_id()][self.get_task_id()])
                text = text.replace("{rights-"+str(i+1)+"}",text_rights)
       
        with open(path+"/zadanie","a") as f:
            f.write(str(self.get_task_id()+1)+". "+text+"\n\n")


    def number_elements(self,command,string):
        """Zisti sa pocet (suborov, adresarov, ciest, pouzivatelskych prav) v ulohe """

        number_element = 0
        count_element = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(string), command))
        for i in range(count_element):
            if (command.find(string+str(i+1)+"}"))!=-1:
                number_element += 1
        return number_element


    def make_text_rights(self,rights):
        """Vytvori sa textovy zapis pouzivatelsky prav """

        text_rights = ""
      
        for one in rights[0]:
 
            if one == 4 or one == 6 or one == 5 or one == 7:
            
                text_rights += "R"
            else:
                text_rights += "-"
           
            if one == 2 or one == 3 or one == 6 or one == 7:
                text_rights += "W"
            else:
                text_rights += "-"
            
            if one == 1 or one == 3 or one == 5 or one == 7:
                text_rights += "X"
            else:
                text_rights += "-"
            
            text_rights += " "
            
        return text_rights


    def make_path(self,path):
        """Vytvori sa cesta """

        path_complete = path
        os.makedirs(path_complete,exist_ok=True,mode=0o777)
        os.system("sudo chown "+self.get_students_names()[self.get_student_id()]+" "+path_complete)
        subprocess.call(['chmod', '-R', '777', "/home/"+self.get_students_names()[self.get_student_id()]])
        os.chmod("/home/"+self.get_students_names()[self.get_student_id()],0o700)


    def create_users(self):
        """Vytvoria sa pouzivatelia pre studentov """

        encrypt_password = crypt.crypt(self.get_test_password(),"22")
        
        for i in range(self.get_number_students()):

            os.system("sudo useradd -m -s /bin/bash -p"+ encrypt_password + " " + self.get_students_names()[i])
            os.system("sudo usermod -a -G students "+self.get_students_names()[i])
            os.chmod("/home/"+self.get_students_names()[i],0o700)
            

    def remove_users(self,name):
        """Vymazu sa pouzivatelia pre studentov """

        path = self.get_system_path()+"tests_files/"+name+"/test_info.csv"
        self.read_test_info(path)

        for i in range(self.get_number_students()):
            os.chmod("/home/"+self.get_students_names()[i],0o777)
            os.system("sudo userdel -r "+self.get_students_names()[i])
            os.system("sudo rmdir /home/"+self.get_students_names()[i])


    def remove_only_student_enviroment(self,test_name):
        """Vymaze sa iba prostredie v ktorom student pracuje teda je ho domovsky adresar """

        path = self.get_system_path()+"tests_files/"+test_name+"/test_info.csv"
        self.read_test_info(path)

        for i in range(int(self.get_number_students())):         
            if self.exist_user(self.get_students_names()[i]) == True:
                self.remove_enviroment_student("/home/"+self.get_students_names()[i]+"/")
            else:
                print("> User "+self.get_students_names()[i]+" not exist.")


    def remove_backup_files(self,test_name):
        """Vymazu sa iba subory v zalohe """
        path = self.get_system_path()+"tests_files/"+test_name+"/test_info.csv"
        self.read_test_info(path)
        
        for i in range(int(self.get_number_students())):         
            self.remove_enviroment_student(self.get_system_path()+"tests_files/"+self.get_name_test()+"/")


    def two_d_array_int(self,x,y):
        """Vytvory sa ciselne dvojrozmerne pole """

        two_d_array = []
        for i in range(x):
            temp = []
            for j in range(y):
                temp.append(0)
            two_d_array.append(temp)
        return two_d_array


    def number_files_in_array(self,array):
        """Zisti sa pocet suborov, ciest, adresarov, pouzivatelskych prav a ich mena """
        pocet = 0
        temp = []
        help = False
        for prvok in array:
            help = False
            if type(prvok) is str:
                for tmp_prv in temp:
                    if tmp_prv == prvok:
                        help = True
                if help == False:
                    pocet += 1
                    temp.append(prvok)                 
        return pocet,temp

    

    def remove_enviroment(self):
        """Spusti vymazanie suborov, ktore sa nachadzaju v domovskych adresaroch studentov a ulozene kopie pre kontrolu """

        for i in range(self.get_number_students()):         
            if self.exist_user(self.get_students_names()[i]) == True:
                self.remove_enviroment_student("/home/"+self.get_students_names()[i]+"/")
                self.remove_enviroment_student(self.get_system_path()+"tests_files/"+self.get_name_test()+"/")
            else:
                print("> User "+self.get_students_names()[i]+" not exist.")
       

    def remove_enviroment_student(self,folder):
        """Vymaze subory studenta a ulozene kopie pre kontrolu """
            
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

        dir=self.get_system_path()+"tasks"
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

    def get_array_for_action(self):
        return self.array_for_action

    def set_array_for_action(self,array_for_action):
        self.array_for_action = array_for_action
        
    def get_generate_file_names(self):
        return self.generate_file_names

    def get_generate_path_names(self):
        return self.generate_path_names

    def get_generate_dir_names(self):
        return self.generate_directory_names

    def get_generate_rights_names(self):
        return self.generate_rights_names

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

