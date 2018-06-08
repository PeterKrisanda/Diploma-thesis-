"""Timer modul

Tento modul spusti casovac testu a po jeho uplynuti sa vyhodnoti test,
jeho vysledok sa zapise do csv suboru, a ulozi sa vysledok pre studenta.
"""
import time
import os
import csv
import datetime
from pathlib import Path
from evaluator import Evaluator
from testmaker import TestMaker


class Timer:

    def __init__(self):
        self.students_names = []
        self.test_maker = TestMaker()
    
    def time(self,name,set_time,output):
        """Spusti sa casovac, po uplynuti casu sa spusti vyhodnotenie """
        
        set_time = self.read_info(name,set_time)
        minute_set_time = int(set_time)
        set_time = int(set_time)
        set_time *= 60
        endTest = 0
        self.allow_students_write(name)
        while endTest == 0:
            print("\n\nTime start.")
            test_maker = TestMaker()
            test_maker.actual_test(name)
            self.set_remaining_time(name,minute_set_time)
            time.sleep(set_time)
            endTest = 1

        print("\n\nTime out. Evaluating test.") 

        self.disallow_students_write(name)
        evaluator = Evaluator()
        evaluator.evaluate(name,None)
        evaluator.write_evaluation()
        evaluator.make_evaluate_file()
        if output:
            evaluator.print_evaluate(None)
        
        self.remove_remaining_time(name)
            
        
    def read_info(self,name,set_time):
        """Nacita sa z csv subora cas testu, ktory sa vrati. Nacitaju sa mena studentov. """

        students_names = []
        if name != None:           
            path = (self.get_system_path()+"tests_files/"+name+"/test_info.csv")
            if Path(path).exists():
                with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                    reader = csv.DictReader(csv_file,delimiter=';')
                    for row in reader:
                        if row['Name'] == "all.students" and set_time == None:                    
                            set_time = row['Time']

                        if row['Name'] != "all.students" and row['Name'] != "":
                            students_names.append(row['Name'])
            else:
                print("File with test info not exist.")
        else:
            print("Missing argument test name.")
        self.set_students_names(students_names)
        return set_time

    def get_remaining_time(self,name_test):
        """Ziskanie aktualneho casu od konca testu a jeho vypis """
 
        if name_test != None:
            (end_hours,end_minutes,end_seconds)=self.read_end_time(name_test)
            time = datetime.datetime.now()
            hours = int(time.hour)
            minutes = int(time.minute)
            seconds = int(time.second)
            if end_hours != "" and end_minutes != "" and end_seconds != "":
                self.calculate_remaining_time(end_hours,end_minutes,end_seconds)

        else:
            print("Missing argument name test.")
        
    def set_remaining_time(self,name,set_time):
        """Nastavi sa aktualny cas a cas po ukoncenia testu """

        path = self.get_system_path()+"tests_files/"+name+"/remaining_time.csv"
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"w",encoding = "ISO-8859-1") as csv_file:
            field_names = ['Time','Time_start','Time_end']
            writer = csv.DictWriter(csv_file, fieldnames = field_names,delimiter=';')
            writer.writeheader()
            time = datetime.datetime.now()
            (hours,minutes)=self.make_end_time(time,set_time)
            writer.writerow({'Time':'hours','Time_start':time.hour,'Time_end':hours})
            writer.writerow({'Time':'minutes','Time_start':time.minute,'Time_end':minutes})
            writer.writerow({'Time':'seconds','Time_start':time.second,'Time_end':time.second})


    def make_end_time(self,time,set_time):
        """Vypocita sa šas ukončenia testu """

        minutes = int(time.minute)
        hours = int(time.hour)
        minutes += set_time
        while minutes > 59:
           hours += 1
           minutes -= 60

        return (hours,minutes)

    def read_end_time(self,name_test):
        """Nacita sa cas ukoncenia testu """

        path = self.get_system_path()+"tests_files/"+name_test+"/remaining_time.csv"
        if Path(path).exists():
            with open(path,"r",encoding = "ISO-8859-1") as csv_file:
                reader = csv.DictReader(csv_file,delimiter=';')
                for row in reader:
                    if row['Time'] == 'hours' and row['Time_end'] != "":
                        end_hours = row['Time_end']
                    if row['Time'] == 'minutes' and row['Time_end'] != "":
                        end_minutes = row['Time_end']
                    if row['Time'] == 'seconds' and row['Time_end'] != "":
                        end_seconds = row['Time_end']
        else:
            print("No timer started")
            end_hours = ""
            end_minutes = ""
            end_seconds = ""
        return (end_hours,end_minutes,end_seconds)

    def calculate_remaining_time(self,end_hours,end_minutes,end_seconds):
        """Vypocita sa zostavajuci cas do ukoncenia testu """
        time = datetime.datetime.now()
        hours = int(time.hour)
        minutes = int(time.minute)
        seconds = int(time.second)
        remaining_hours = int(end_hours) - int(time.hour)
        remaining_minutes = int(end_minutes) - int(time.minute)
        remaining_seconds = int(end_seconds) - int(time.second)
        if remaining_seconds < 0:
            remaining_seconds = 60 + remaining_seconds
            remaining_minutes -= 1
        if remaining_minutes < 0:
            remaining_minutes = 60 + remaining_minutes
            remaining_hours -= 1

        if remaining_hours < 0:
            remaining_hours = 0
            remaining_minutes = 0
            remaining_seconds = 0
 
        print("Remaining time: "+"{0:0=2d}".format(remaining_hours)+":"+"{0:0=2d}".format(remaining_minutes)
                +":"+"{0:0=2d}".format(remaining_seconds))

    def remove_remaining_time(self,name_test):
        """Vymaze sa pomocni subor pre zostavajuci cas do ukoncenia testu """

        path = self.get_system_path()+"tests_files/"+name_test+"/remaining_time.csv"
        os.system("sudo rm -rf "+path)
                    

    def allow_students_write(self,name_test):
        """Povoli sa studentovi zapisovat do vzdialeneho repozitara. """

        rights = "777"
        self.change_students_rights(rights,name_test)

    def disallow_students_write(self,name_test):
        """Zakaze sa studentovi zapisovat do vzdialeneho repozitara. """

        rights = "555"
        self.change_students_rights(rights,name_test)

    def change_students_rights(self,rights,name_test):
        """Zmenia sa prava vzdialeneho repozitara pre studenta. """

        for student_name in self.get_students_names():
            path = "/home/"+student_name+"/student/project_"+student_name+".git/."
            os.system("sudo chmod -R "+rights+" "+path)


    def get_students_names(self):
        return self.students_names

    def set_students_names(self,students_names):
        self.students_names = students_names

    def get_system_path(self):
        path_to_system = os.path.realpath(__file__)
        return self.test_maker.check_something(path_to_system,"","timer.py")
