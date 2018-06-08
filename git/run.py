#!/usr/bin/env python3
"""Run modul
 
Tento modul nam vyberie podla argumentov co sa ma vykonat.
Moze sa vytvorit test, vyhodnotit, spustit casovac a mozu sa vymazat 
uz nepouzivany pouzivatelia.
"""

from parser import Parser
from testmaker import TestMaker
from evaluator import Evaluator
from timer import Timer
import argparse
from pathlib import Path


def check_users_exist(test_maker):
    """Funkcia nam zisti ci existuju pouzivatelia """
    all_users_exist = True
    for i in range(test_maker.get_number_students()):
        all_users_exist = all_users_exist and test_maker.exist_user(test_maker.get_students_names()[i])  
    return all_users_exist

def definition_arguments():
    """Funkcia pre definovanie argumentov """

    arg_parser = argparse.ArgumentParser()
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument('-c','--create',action="store_true",help='Create test')
    group.add_argument('-e','--evaluate',action="store_true",help='Evaluate test')
    group.add_argument('-r','--remove',action="store_true",help='Remove users')
    group.add_argument('--start', action="store_true",help='Start test time')
    group.add_argument('--remaining_time',action="store_true",help='Show remaining time.')
        
    arg_parser.add_argument('-f','--file',type=str,help='Path to file for create test')
    arg_parser.add_argument('-n','--name',type=str,help='Name test')
    arg_parser.add_argument('-s','--student',type=str,help='Login student')
    arg_parser.add_argument('-u','--users',action="store_true",help='Option users')
    arg_parser.add_argument('-o','--output',action="store_true",help='Output of evaluation')
    arg_parser.add_argument('-w','--write',action="store_true",help='Write evaluation to file')
    arg_parser.add_argument('-t','--time',type=int,help='Set time for test in minutes.')
    arg_parser.add_argument('-b','--backup',action="store_true",help="Remove backup")
        
    return arg_parser.parse_args()

def create_test(args):
    """Metoda pre vytvorenie testu """

    path = Path(args.file)

    if path.exists():
        test_maker = TestMaker()
        parser = Parser(str(args.file))
        parser.parse("")
        path_info = parser.write_test_info()
     
        test_maker.read_test_info(path_info)
        
        if args.users:
            test_maker.create_users()
        
        if check_users_exist(test_maker):
            generate_tasks = test_maker.generate_tasks(path_info)
            if generate_tasks != "error":
                test_maker.create_projects_for_test()
            
                test_maker.create_tasks(parser)
            else:
                print("Error count task is bigger then max task.")
        else:
            print("Users not exist.")
        

    else:
        print("File not exist.")


def main():

    evaluator = Evaluator()
    test_maker = TestMaker()
    timer = Timer()
     
    args = definition_arguments()
        
    if args.create:
        create_test(args)
    
    elif args.evaluate:
        evaluator.evaluate(args.name,args.student)
        if args.write:
            evaluator.write_evaluation()
        if args.output:
            evaluator.print_evaluate(args.student)
        evaluator.make_evaluate_file()
    
    if args.remove:
        if args.users == False:
            test_maker.remove_only_student_enviroment(args.name)
        if args.users:
            test_maker.remove_users(args.name)
        if args.backup:
            test_maker.remove_backup_files(args.name)
    
    elif args.start:
        timer.time(args.name,args.time,args.output)
    elif args.remaining_time:
        timer.get_remaining_time(args.name)
    
if __name__ == '__main__':
    main()

