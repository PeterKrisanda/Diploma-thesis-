"""Module3

Definovanie ulohy - Student ma prepisat urceny riadok suboru v urcenej vetve. Po prepisani tohto
suboru posle vetvy do vzdialeneho repozitara. Vznikne konflikt pretoze niekto urobil zmenu v rovnakom
subore. Student musi vyriesit tento konflikt. Ma pouzit svoju verziu suboru a vetvu s novou verziou
suboru zapisat do vzdialeneho repozitara.
"""

from gitmaker import GitMaker

class Tasks(GitMaker):

    def __init__(self,*args):
        super().__init__(args)

        self.branch_1 = self.select_branch_name()
        self.file_1 = self.select_file_name()
        self.text_file_1 = self.select_text_for_file(self.file_1)

    def define_task_text(self):

        text = ("Vo vetve {} v subore {} prepiste {}. Poslite vetvu {} do vzdialeneho "
        +"repozitara.Vyrieste konflikt pricom pouzite vasu verziu suboru.").format(self.branch_1
        ,self.file_1,self.text_file_1,self.branch_1)

        return text
        

    def create_student_start_repository(self):
       
        self.make_branch_to_student_project_from_branch(self.branch_1,"master")
        self.make_file_to_student_branch(self.branch_1,self.file_1)
        

    def change_repository_before_first_push(self):

        self.modify_file_in_student_branch(self.branch_1,self.file_1)
                

    def create_correct_solution_project(self):
        
        self.make_branch_to_correct_solution_from_branch(self.branch_1,"master")
        self.make_file_to_correct_solution_branch(self.branch_1,self.file_1)
        

    def evaluate_task(self):
  
        return self.compare_student_and_correct_solution_branches(self.branch_1,self.branch_1)

