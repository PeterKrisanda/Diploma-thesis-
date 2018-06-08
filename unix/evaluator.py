"""Evaluator modul
 
Tento modul nam vyhodnoti test podla informacii, ktore sa nachadzaju
v pomocnych csv suboroch pre vyhodnotenie.
"""
from parser import Parser
from testmaker import TestMaker
import os
import stat
import re
import csv
import filecmp
from pathlib import Path

class Evaluator:
    
    test_maker = TestMaker()

    def __init__(self):
        self.array_for_points = []
        self.array_for_evaluate = []
        self.number_students = 0
        self.students_names  = []
        self.name_test = "defaultName"
        self.count_tasks = ""
        self.student_id = 0
        self.task_id = 0
        self.parser = Parser("")
        

    def evaluate(self,name_test):
        """Spusti sa nacitanie informacii o teste a zacne sa vyhodnotenie pre vsetkych studentov """

        self.set_parser(self.parser)
        self.set_test_maker(self.test_maker)
        self.read_test_info(name_test)
        self.set_array_for_points(self.make_array_points(int(self.get_number_students()),int(self.get_count_tasks())))      

        for i in range(self.get_number_students()):
            self.set_student_id(i)

            for j in range(int(self.get_count_tasks())):
                self.set_task_id(j)
                self.evaluate_task_for_student()


    def evaluate_task_for_student(self):
        """Zacne sa vyhodnotenie konkretnej ulohy pre konkretneho studenta """

        help = []
        self.set_array_for_evaluate(help)
        self.read_evaluate_info_for_task("tests_files/"+self.get_name_test()+"/"+(self.get_students_names()
                                        [self.get_student_id()])+"/evaluate_info-"+str(self.get_task_id()+1)+".csv")
        self.evaluate_task()
        

    def read_evaluate_info_for_task(self,path):
        """Nacita sa zo suboru csv info pre vyhodnotenie ulohy """

        path = self.get_system_path() + path

        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                array_for_read = []
            
                for row in reader:
                    for head in header:
                        if head != "files" and head != "name" and row[head] != "":
                            array_for_read.append(head)
                            temp = []
                            temp.append(row['files'])
                            temp.append(row[head])
                            array_for_read.append(temp)
                self.get_array_for_evaluate().append(array_for_read)
        else:
            print("File with evaluate info not exist.")
         

    def evaluate_task(self):
        """Spustia sa akcie pre jednotlive moznosti vyhodnotenia """

        actual_prvok=""
        par = []

        actual_action = ""
        for array in self.get_array_for_evaluate():
            for item in array:
                if type(item) is str:
                    actual_action = item
                elif type(item) is list:
                    if actual_action == "exist_in":
                        par = self.append_parameters(par,item)
                        self.exist_in(par,True)
                        par = []
                 
                    elif actual_action == "not_exist_in":
                        par = self.append_parameters(par,item)
                        self.exist_in(par,False)
                        par = []
                  
                    elif actual_action == "compare":
                        par = self.append_parameters(par,item)
                        self.compare(par)
                        par = []
                        
                    elif actual_action == "command":
                        par = self.append_parameters(par,item)      
                        self.command(par)  
                        par = [] 
                        
                    elif actual_action == "have_rights":
                        par = self.append_parameters(par,item)
                        self.have_rights(par)
                        par = []
                  
                else:
                    print("error")


    def append_parameters(self,parameter,items):
        """Pomocna funkcia ktora pripoji parametre akcie do pola """

        for item in items:
            parameter.append(item)  
        return parameter


    def exist_in(self,par,have_exist):
        """Metoda vyhodnoti ci existuje alebo nie na urcenom mieste zadany subor """

        par[0] = par[0] + "-"
        par[1] = par[1] + "-"

        if (par[0].find("file-"))!=-1:
            file_or_directory_id = self.get_id(par[0],"file-")
            string_id_to_read = "file-"
        elif (par[0].find("directory-"))!=-1:
            file_or_directory_id = self.get_id(par[0],"directory-")
            string_id_to_read = "directory-"
    
        path_id = self.get_id(par[1],"path-")
       
        need_path = self.read_name(path_id,"path-")
        if need_path == None:
            need_path = ""
            
        path = Path("/home/"+self.get_students_names()[self.get_student_id()]+"/"+need_path
                    +self.read_name(file_or_directory_id,string_id_to_read) )    
        is_in_path = path.exists()

        if is_in_path == True:
            if have_exist == True:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 1)

            else:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 0)
        else:
            if have_exist == False:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 1)

            else:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 0)

    
    def compare(self,par):
        """Porovna obsah suboru z kopiou suboru """

        actual_action = ""
        need_path = ""
        help = False
        
        for action in self.get_array_for_evaluate()[0]:
            if type(action) is str:
                actual_action = action
            elif type(action) is list:
                if actual_action == "exist_in" and par[0] == action[0]:
                    need_path = action[1]
            else:
                print("type error")

         
        need_path += "-"
        par[0] = par[0] + "-"
        par[1] = par[1] + "-"

        file_student_id = self.get_id(par[0],"file-")
        file_save_id = self.get_id(par[1],"file-")

        need_path_id = self.get_id(need_path,"path-")
        need_path = self.read_name(need_path_id,"path-")

        if need_path == None:
            need_path = ""
                 
        path_student_file = need_path + self.read_name(file_student_id,"file-")
        path_save_file = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]
                        +"/files/"+self.read_name(file_save_id,"file-"))

        path_student_file = "/home/"+self.get_students_names()[self.get_student_id()]+"/"+path_student_file
        if Path(path_student_file).exists():
            if filecmp.cmp(path_student_file,path_save_file) == True:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 1)
                
            else:
                self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
                [self.get_student_id()][self.get_task_id()] and 0)
                
        else:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
            [self.get_student_id()][self.get_task_id()] and 0)

        
    def command(self,par):
        """Porovna spravny prikaz pre ulohu z prikazmi zadanymi studentom """

        command = par[1]
        no_path = False
        par[0] = par[0] + "-"
     
        need_path = ""
        if par[0].find("path-") != -1 and par[0] != "no_path-":        
            need_path_id = self.get_id(par[0],"path-")
            if self.read_name(need_path_id,"path-") != None:
                need_path = ("/home/"+self.get_students_names()[self.get_student_id()] +"/"
                            +self.read_name(need_path_id,"path-"))
            else:
                need_path = ""

        elif par[0] == "home-":
            need_path = "/home/"+self.get_students_names()[self.get_student_id()]+"/"
        elif par[0] == "no_path-":
            no_path = True
        else:
            print("wrong par[0]")
        
        correct_command = self.make_command_with_names(command)
        

        correct = False
        with open("/var/log/commands.log","r") as file:
            line = file.readline()
            while(line):
                if line.find("/home/"+self.get_students_names()[self.get_student_id()]) != -1:
                    actual_command = self.check_command(line)
                    actual_command = ''.join(actual_command)
                    actual_path = self.check_path(line)
                    actual_path = ''.join(actual_path) + "/"

                    if ((actual_command == correct_command and actual_path == need_path) 
                        or (actual_command == correct_command and no_path == True) 
                        or (actual_command == correct_command and need_path == actual_path)):                    
                        correct = True
                line = file.readline()

        if correct == True:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
            [self.get_student_id()][self.get_task_id()] and 1)
        else:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
            [self.get_student_id()][self.get_task_id()] and 0)
        
        
    def have_rights(self,par):
        """Vyhodnoti ci subor v ulohe ma urcene pouzivatelske prava """
  
        need_path = self.get_path_for_file(par[0])
        
        par[0] += "-"
        par[1] += "-"
        need_path += "-"

        file_student_id = self.get_id(par[0],"file-")
        file_name = self.read_name(file_student_id,"file-")

        rights_id = self.get_id(par[1],"rights-")
        rights_number = self.read_name(rights_id,"rights-")
     
        need_path_id = self.get_id(need_path,"path-")
        need_path = self.read_name(need_path_id,"path-")
     
        list_rights = []
        list_rights.append(re.findall(r'\d+',rights_number))
        correct_rights = "0"
        for i in range(3):
            correct_rights += list_rights[0][i]
        file_to_control = "/home/"+self.get_students_names()[self.get_student_id()]+"/" + need_path + file_name
    
        st = os.stat(file_to_control)
        oct_perm = oct(st.st_mode)
        perm = oct_perm[-4:]

        if perm == correct_rights:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
            [self.get_student_id()][self.get_task_id()] and 1)
        else:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = (self.get_array_for_points()
            [self.get_student_id()][self.get_task_id()] and 0)
    

    def get_path_for_file(self,parameter):
        """Pomocna funkcia zisti cestu, v ktorej sa ma nachadzat subor """

        path = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]
                +"/create_info-"+str(self.get_task_id()+1)+".csv")
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                for row in reader:
                    if row['locate_in'] != "" and row['files'] == parameter:
                        need_path = row['locate_in']
        else:
            print("File with create info not exist.")
            need_path = ""
        return need_path
        

    def get_id(self,parameter,string):
        """Zisti id suboru, adresara, cesty, pouzivatelskych prav """

        id = self.get_parser().check_something(parameter,string,"-")
        return int(id) - 1

    def make_command_with_names(self,command):
        """Prepise v prikaze mena na skutocne vygenerovane mena """

        file_in_system = "tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]+"/files/"
        number_file = self.get_test_maker().number_elements(command,"file-")        
        number_path = self.get_test_maker().number_elements(command,"path-")
        number_directory = self.get_test_maker().number_elements(command,"directory-")
        number_absolute = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape("absolute"), command))        

        file_names = self.append_names(number_file,"file-")
        path_names = self.append_names(number_path,"path-")
        directory_names = self.append_names(number_directory,"directory-")
        correct_command = command

        for i in range(number_file):
            correct_command = correct_command.replace("{file-"+str(i+1)+"}",str(file_names[i]))   
        for i in range(number_path):
            correct_command = correct_command.replace("{path-"+str(i+1)+"}",str(path_names[i]))
        for i in range(number_directory):
            correct_command = correct_command.replace("{directory-"+str(i+1)+"}",str(directory_names[i]))
        for i in range(number_absolute):
            correct_command = correct_command.replace("{absolute}","/home/"+self.get_students_names()[self.get_student_id()]+"/")
        if correct_command.find("{system}") != -1:
            correct_command = correct_command.replace("{system}",file_in_system)

        return correct_command


    def check_command(self,line):
        """Vytiahne prikaz zadany studentom """

        return re.findall(r']: (.*?) \[',line)


    def check_path(self,line):
        """Zisti cestu z ktorej bol pouzity prikaz """

        return re.findall(r'] \[(.*?)\]',line)


    def append_names(self,num,string):
        """Pridaju sa do pola mena suborov, adresarov, cesty """

        array = []
        for i in range(num):
            if self.read_name(i,string) != None:
                array.append(self.read_name(i,string))
            else:
                array.append("")
        return array


    def write_evaluation(self):
        """Zapisu sa body, ktore studenti ziskali do suboru """

        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/test_info.csv"
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                for row in reader:
                    if row['Name Export File'] != "" and row['Name'] == "all.students":
                        path_to_export = row['Name Export File']
        else:
            print("File with test info not exist.")
        os.makedirs(os.path.dirname(path_to_export),exist_ok=True)
        with open(path_to_export,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Login','Tasks Points','Points']
            
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            for i in range(int(self.get_number_students())):
                student_points = 0
                for j in range(int(self.get_count_tasks())):
                    student_points = student_points + self.get_array_for_points()[i][j]
                writer.writerow({'Login':self.get_students_names()[i],'Tasks Points':self.get_array_for_points()[i],
                                'Points':student_points})

                
    def read_name(self,id,file_or_path):
        """Nacitaju sa mena z csv suboru """

        path_info = (self.get_system_path()+"tests_files/"+self.get_name_test()+"/"+self.get_students_names()[self.get_student_id()]
                    +"/evaluate_info-"+str(self.get_task_id()+1)+".csv")
        if Path(path_info).exists():
            with open(path_info,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames
                for row in reader:
                    if row['name'] != "" and row['files'] == (file_or_path+str(id+1)):
                        return row['name']
        else:
            print("File with evaluate info not exist.")
            return ""


    def read_test_info(self,name_test):
        """Nacitaju sa potrebne info o teste """
 
        path_info = self.get_system_path()+"tests_files/"+name_test+"/test_info.csv"
 
        students_names = []
        number_students = 0
        if Path(path_info).exists():
            with open(path_info,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                for row in reader:
                    if row['Name'] == "all.students":
                        self.set_count_tasks(row['Count Tasks'])
                        self.set_name_test(row['Name Test'])
                    elif row['Name'] != "all.students" and row['Name'] != "":
                        students_names.append(row['Name'])
                        number_students += 1
        else:
            print("File with test info not exist.")

        self.set_number_students(number_students)
        self.set_students_names(students_names)


    def print_evaluate(self,name):
        """Spusti sa vypisanie hodnotenia studentov na standardny vystup """
 
        for i in range(int(self.get_number_students())):
            student_points = 0
            for j in range(int(self.get_count_tasks())):
                student_points += self.get_array_for_points()[i][j]
            if self.get_students_names()[i] == name:
                self.print_student_evaluate(student_points,i)
            if name == None:
                self.print_student_evaluate(student_points,i)

    
    def print_student_evaluate(self,student_points,i):
        """Posklada sa sprava vyhodnotenia studentov a vypise sa na standardny vystup """

        name = self.get_students_names()[i]+": "
        message = str(self.get_array_for_points()[i])+", Total points: "+str(student_points)
        print("{:<25}".format(name)+message)


    def send_message(self):
        """Posle sa sprava studentovy o jeho hodnoteni """
        
        for i in range(int(self.get_number_students())):
            message = self.create_message(i)
            os.system("sudo mesg y")
            os.system("sudo echo \""+str(message)+"\" 2> /dev/null | write "+self.get_students_names()[i]+" 2> /dev/null")
            

    def create_message(self,student_id):
        """Posklada sa sprava pre studenta o jeho hodnoteni """

        points = 0
        message = ""
        for i in range(int(self.get_count_tasks())):
            message += "Uloha "+str(i+1)+" : "+str(self.get_array_for_points()[student_id][i])+"\n"    
            points += self.get_array_for_points()[student_id][i]    

        message = "\nCas vyprsal. \nVase celkove hodnotenie: "+str(points)+"\n" + message    
        return message


    def make_array_points(self,x,y):
        """Vytvori dvojrozmerne pole pre bodove ohodnotenie studentov """

        two_d_array = []
        for i in range(x):
            temp = []
            for j in range(y):
                temp.append(1)
            two_d_array.append(temp)
        return two_d_array


    def get_parser(self):
        return self.parser

    def set_parser(self,parser):
        self.parser = parser

    def get_test_maker(self):
        return self.test_maker

    def set_test_maker(self,test_maker):
        self.test_maker = test_maker

    def get_array_for_points(self):
        return self.array_for_points

    def set_array_for_points(self,array_for_points):
        self.array_for_points = array_for_points

    def get_array_for_evaluate(self):
        return self.array_for_evaluate

    def set_array_for_evaluate(self,array_for_evaluate):
        self.array_for_evaluate = array_for_evaluate

    def get_number_students(self):
        return self.number_students

    def set_number_students(self,number_students):
        self.number_students = number_students

    def get_students_names(self):
        return self.students_names

    def set_students_names(self,students_names):
        self.students_names = students_names

    def get_name_test(self):
        return self.name_test

    def set_name_test(self,name_test):
        self.name_test = name_test

    def get_count_tasks(self):
        return self.count_tasks

    def set_count_tasks(self,count_tasks):
        self.count_tasks = count_tasks

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
        return self.parser.check_something(path_to_system,"","evaluator.py")