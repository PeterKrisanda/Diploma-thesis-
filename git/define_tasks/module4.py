"""Module4

Definovanie ulohy - Student ma za ulohu vytvorit novu vetvu z vetvy master.
V tejto vetve ma vytvorit prazdny subor a zapisat vetvu do vzdialeneho repozitara.
Vznikne konflikt pretoze niekto zapise do vetvy iny subor. Student musi vyriesit
tento konflikt a znova zapisat uspesne vetvu do vzdialeneho repozitara.
"""

from gitmaker import GitMaker

class Tasks(GitMaker):  

    def __init__(self,*args):        
        super().__init__(args)

        self.branch = self.select_branch_name()
        self.file_1 = self.select_file_name()
        self.file_2 = self.select_file_name()

    def define_task_text(self):

        text = ("Vytvorte vetvu {} z vetvy master. Vo vytvorenej vetve vytvorte prazdny subor {}."
        +" Vyrieste konflikty.").format(self.branch,self.file_1)

        return text

    def create_student_start_repository(self):      
        pass

    def change_repository_before_first_push(self):

        self.make_empty_file_to_student_branch(self.branch,self.file_2)


    def create_correct_solution_project(self):
        
        self.make_branch_to_correct_solution_from_branch(self.branch,"master")
        self.make_empty_file_to_correct_solution_branch(self.branch,self.file_1)
        self.make_empty_file_to_correct_solution_branch(self.branch,self.file_2)
        

    def evaluate_task(self):

        return self.compare_student_and_correct_solution_branches(self.branch,self.branch)