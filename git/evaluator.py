"""Evaluator modul
 
Tento modul sa pouziva na pripravu zapis a vypis vyhodnotenia.
"""
from parser import Parser
import os
import csv
from pathlib import Path
import importlib


class Evaluator:

    parser = Parser("")

    def __init__(self):
        self.array_for_points = []
        self.number_students = 0
        self.students_names  = []
        self.name_test = "defaultName"
        self.count_tasks = ""
        self.student_id = 0
        self.task_id = 0
        

    def evaluate(self,name_test,student_to_evaluate):
        """Spusti sa nacitanie informacii o teste a zacne sa vyhodnotenie pre studentov """

        self.read_test_info(name_test)
        self.set_array_for_points(self.make_array_points(int(self.get_number_students()),int(self.get_count_tasks())))      

        for i in range(self.get_number_students()):
            self.set_student_id(i)
            
            for j in range(int(self.get_count_tasks())):
                self.set_task_id(j)
                if student_to_evaluate == None:
                    self.evaluate_task_for_student()
                if student_to_evaluate == self.get_students_names()[self.get_student_id()]:
                    self.evaluate_task_for_student()


    def evaluate_task_for_student(self):
        """Zacne sa vyhodnotenie konkretnej ulohy pre konkretneho studenta """
       
        name_module = self.read_tasks_name()
        name_module = self.parser.check_something(name_module,"",".py")
        TASK_NAME = "define_tasks." + name_module
        tasks_module = importlib.import_module(TASK_NAME,".")
        task = tasks_module.Tasks(self.get_student_id(),self.get_task_id(),self.get_name_test())
        point = task.evaluate_task()

        if point == True:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = 1
        else:
            self.get_array_for_points()[self.get_student_id()][self.get_task_id()] = 0 
   

    def read_tasks_name(self):
        """Nacita nazvy uloh  """
        ulohy = []
        path = self.get_system_path()+"tests_files/"+self.get_name_test()+"/test_info.csv"
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                header = reader.fieldnames

                for row in reader:
                    for head in header:
                        if row['Name'] == self.get_students_names()[self.get_student_id()]:
                            """ """
                            ulohy = row['Tasks Index']
        else:
            print("File with test info not exist.")
        ulohy = ulohy.replace("[", "").replace("]","").replace("\'","").replace(" ","")
        ulohy = ulohy.split(',')
        return ulohy[self.get_task_id()]


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
        print()
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


    def make_evaluate_file(self):
        """Vytvori sa subor s hodnotenim pre studenta """
        
        for i in range(int(self.get_number_students())):
            message = self.create_message(i)
            path = "/home/"+self.get_students_names()[i]+"/hodnotenie"
            with open(path,"w") as file:
                file.write(message)            
            

    def create_message(self,student_id):
        """Posklada sa sprava pre studenta o jeho hodnoteni """

        points = 0
        message = ""
        for i in range(int(self.get_count_tasks())):
            message += "Uloha "+str(i+1)+" : "+str(self.get_array_for_points()[student_id][i])+"\n"    
            points += self.get_array_for_points()[student_id][i]    

        message = "Vase celkove hodnotenie: "+str(points)+"\n" + message    
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

    def get_array_for_points(self):
        return self.array_for_points

    def set_array_for_points(self,array_for_points):
        self.array_for_points = array_for_points

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