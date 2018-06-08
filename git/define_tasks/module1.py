"""Module1

Definovanie ulohy - V tejto ulohe ma student vytvorit novu vetvu z urcenej vetvy.
V tejto vetve ma vytvorit novy subor a zapisat vetvu do vzdialeneho repozitra.
"""
from gitmaker import GitMaker

class Tasks(GitMaker):  

    def __init__(self,*args):        
        super().__init__(args)

        self.branch_1 = self.select_branch_name()
        self.branch_2 = self.select_branch_name()
        self.file_1 = self.select_file_name()

    def define_task_text(self):

        text = ("Vytvorte novu vetvu {} z vetvy {}. V tejto vetve vytvorte prazdny subor "
        +"z nazvom {}. Poslite novu vetvu {} do vzdialeneho repozitara.").format(self.branch_2
        ,self.branch_1,self.file_1,self.branch_2)

        return text


    def create_student_start_repository(self):
               
        self.make_branch_to_student_project_from_branch(self.branch_1,"master")


    def change_repository_before_first_push(self):

        pass


    def create_correct_solution_project(self):
        
        self.make_branch_to_correct_solution_from_branch(self.branch_1,"master")
        self.make_branch_to_correct_solution_from_branch(self.branch_2,self.branch_1)
        self.make_empty_file_to_correct_solution_branch(self.branch_2,self.file_1)
        

    def evaluate_task(self):

        return self.compare_student_and_correct_solution_branches(self.branch_2,self.branch_2)
