"""Module2

Definovanie ulohy - V uz vytvorenej vetve ma student vytvorit novy prazdny subor.
Vetvu student zapise do vzdialeneho repozitara. Vznikne konflikt pretoze niekto uz zapise iny
subor do tej istej vetvy. Student musi vyriesit tento konflikt a zapisat vetvu do vzdialeneho
repozitara.
"""

from gitmaker import GitMaker

class Tasks(GitMaker):

    def __init__(self,*args):
        super().__init__(args)

        self.branch_1 = self.select_branch_name()
        self.file_1 = self.select_file_name()
        self.file_2 = self.select_file_name()

    def define_task_text(self):

        text = ("Vo vetve {} vytvorte prazdny subor {}. Zapiste vetvu {} do vzdialeneho repozitara."
        +" Vyrieste konflikty.").format(self.branch_1,self.file_1,self.branch_1)

        return text


    def create_student_start_repository(self):
      
        self.make_branch_to_student_project_from_branch(self.branch_1,"master")
        

    def change_repository_before_first_push(self):

        self.make_empty_file_to_student_branch(self.branch_1,self.file_2)


    def create_correct_solution_project(self):
        
        self.make_branch_to_correct_solution_from_branch(self.branch_1,"master")
        self.make_empty_file_to_correct_solution_branch(self.branch_1,self.file_1)
        self.make_empty_file_to_correct_solution_branch(self.branch_1,self.file_2)
        

    def evaluate_task(self):

        return self.compare_student_and_correct_solution_branches(self.branch_1,self.branch_1)

