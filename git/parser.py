"""Parser modul

Tento modul rozdeli informacie zo vstupnych suborov do csv suborov.
Rozdeli informacie pre vytvorenie testu.
"""
import csv
import re
import os
from pathlib import Path

class Parser:

    def __init__(self,path):
        self.path = path
        self.section_state = ""
        self.students_names = []
        self.name_test = "defaultName"
        self.test_password = "" 
        self.test_time = ""
        self.name_export = ""
        self.count_tasks = ""
        self.task_text = ""


    def parse(self,type_file):
        """Rozdeluje vstupny subor na riadky """
       
        if type_file == "":
            type_file = self.get_path()
        if Path(type_file).exists():
            with open(type_file,"r") as file:
                line = file.readline()
                while(line):
                    self.check_line(line)
                    line = file.readline()
        else:
            print("File to parse not exist.")
        

    def check_line(self,line):
        """Zistuje ci je to subor pre vytvorenie testu """

        section_state = self.check_something(line,"\[","\]")       
 
        if section_state != "":           
            self.set_section_state(section_state)
      
        if self.get_section_state() == "TEST":          
            if section_state != "TEST":
                self.parse_test(line)        
        else:
            print("No section")


    def parse_test(self,line):
        """Rozdeluje a uklada parametre pre vytvorenie testu """
        
        file_name = self.parse_concrete_test_info(line,"users_file")
        if file_name != "not_in_line":
            self.read_students_names(file_name)
     
        test_password = self.parse_concrete_test_info(line,"test_password")
        if test_password != "not_in_line":
            self.set_test_password(test_password)

        test_time = self.parse_concrete_test_info(line,"test_time")
        if test_time != "not_in_line":
            self.set_test_time(test_time)

        name_export = self.parse_concrete_test_info(line,"name_export_file")
        if name_export != "not_in_line":
            self.set_name_export(name_export)

        count_tasks = self.parse_concrete_test_info(line,"count_tasks")
        if count_tasks != "not_in_line":
            self.set_count_tasks(count_tasks)

        name_test = self.parse_concrete_test_info(line,"name_test")
        if name_test != "not_in_line":
            self.set_name_test(name_test)


    def parse_concrete_test_info(self,line,string):
        """Pomocna funkcia ktora ziska konkretny paramter """
      
        is_in_line = line.find(string)
        if is_in_line != -1:    
            info = self.check_something(line,string+"\=\"","\"")
            return info
        else:
            return "not_in_line"


    def read_students_names(self,file_name):
        """Precita mena studentov zo suboru a ulozi ich """
        file_name = self.get_system_path() + file_name

        if Path(file_name).exists():
            with open(file_name,encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                num_students = 0
                for row in reader:
                    is_student = row['E-Mail'].find("@student.tuke.sk")
                    if is_student != -1:
                        num_students+=1
                
            students_names = self.make_string_array(num_students)
            with open(file_name,encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                help = 0
                for row in reader:
                    is_student = row['E-Mail'].find("@student.tuke.sk")
                    if is_student != -1:
                        students_names[help] = self.check_something(row['E-Mail'],"","@student.tuke.sk")
                        students_names[help] = ''.join(students_names[help])
                        help+=1

            self.set_students_names(students_names)
        else:
            print("File with student info not exist")
        
        
    def write_test_info(self):
        """Zapise do csv suboru informacie pre vytvorenie testu """
 
        path_info = self.get_system_path()+"tests_files/"+self.get_name_test()+"/test_info.csv"
        os.makedirs(os.path.dirname(path_info),exist_ok=True)
        with open(path_info,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Name','Password','Time','Name Export File', 'Count Tasks', 'Name Test']
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            writer.writerow({'Name':'all.students','Password':self.get_test_password(),'Time':self.get_test_time(),
                            'Name Export File':self.get_name_export(),'Count Tasks':self.get_count_tasks(),
                            'Name Test':self.get_name_test()})
            for student_name in self.get_students_names():
                writer.writerow({'Name':student_name})
        return path_info


    def check_something(self,line,before,behind):
        """Pomocna funkcia vrati nieco co sa nachadza medzi zadanimi hodnotami v retazci """

        some_string = re.findall(r''+before+'(.*?)'+behind,line)
        some_string = ''.join(some_string)
        return some_string
       

    def make_string_array(self,num):
        """Vytvori jednorozmerne pole """

        array = []
        for i in range(num):
            array.append('')
        return array       
        

    def get_path(self):
        return self.path

    def get_section_state(self):
        return self.section_state

    def set_section_state(self,section_state):
        self.section_state = section_state

    def get_students_names(self):
        return self.students_names

    def set_students_names(self,students_names):
        self.students_names = students_names

    def get_name_test(self):
        return self.name_test

    def set_name_test(self,name_test):
        self.name_test = name_test

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

    def get_task_text(self):
        return self.task_text

    def set_task_text(self,task_text):
        self.task_text = task_text

    def get_system_path(self):
        path_to_system = os.path.realpath(__file__)
        return self.check_something(path_to_system,"","parser.py")