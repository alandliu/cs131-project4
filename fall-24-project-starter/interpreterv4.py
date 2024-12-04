from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
import copy
import sys # TODO: REMOVE REMOVE REMOVE

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output        


    class Thunk:
        def __init__(self, value, interpreter, scopes, evaluated = None):
            self.evaluated = True
            self.interpreter = interpreter
            self.scopes = scopes # The scope in which the thunk was declared
            if evaluated == None or not evaluated:
                self.evaluated = False
            self.value = value
        
        def evaluate(self):
            if self.evaluated:
                return
            if self.value.elem_type in self.interpreter.arithmetic_ops or self.value.elem_type in self.interpreter.comparison_ops or self.value.elem_type in self.interpreter.bool_ops:
                self.value = self.interpreter.evaluate_expression(self.value, self.scopes).value
                self.evaluated = True
            elif self.value.elem_type == self.interpreter.FCALL_NODE:
                ret_thunk, self.scopes = self.interpreter.do_call(self.value, self.scopes)
                self.value = ret_thunk.value
                cur_type = type(self.value)
                if cur_type is not int and cur_type is not bool and cur_type is not str:
                    self.evaluate()
                else:
                    self.evaluated = True

            else:
                self.value = self.interpreter.evaluate_variable_node(self.value, self.scopes).value
                self.evaluated = True
            return
        
        def get_val(self):
            self.evaluate()
            return self
        
        def has_evaluated(self):
            return self.evaluated
        
        def get_type(self):
            return type(self.value)
        
        def __str__(self):
            return "(" + str(self.value) + ", Evaluated: " + str(self.evaluated) + ")"
        
        def __repr__(self):
            return str(self)
        
        def __bool__(self):
            return self.get_val().value
        
        def __add__(self, other):
            return Interpreter.Thunk(self.get_val().value + other.get_val().value, self.interpreter, self.scopes, True)
        
        def __sub__(self, other):
            return Interpreter.Thunk(self.get_val().value - other.get_val().value, self.interpreter, self.scopes, True)
        
        def __mul__(self, other):
            return Interpreter.Thunk(self.get_val().value * other.get_val().value, self.interpreter, self.scopes, True)
        
        def __floordiv__(self, other):
            return Interpreter.Thunk(self.get_val().value // other.get_val().value, self.interpreter, self.scopes, True)
        
        def __lt__(self, other):
            return Interpreter.Thunk(self.get_val().value < other.get_val().value, self.interpreter, self.scopes, True)
        
        def __gt__(self, other):
            return Interpreter.Thunk(self.get_val().value > other.get_val().value, self.interpreter, self.scopes, True)
        
        def __le__(self, other):
            return Interpreter.Thunk(self.get_val().value <= other.get_val().value, self.interpreter, self.scopes, True)
        
        def __ge__(self, other):
            return Interpreter.Thunk(self.get_val().value >= other.get_val().value, self.interpreter, self.scopes, True)
        
        def __eq__(self, other):
            return Interpreter.Thunk(self.get_val().value == other.get_val().value, self.interpreter, self.scopes, True)
        
        def __ne__(self, other):
            return Interpreter.Thunk(self.get_val().value != other.get_val().value, self.interpreter, self.scopes, True)
        
        def __neg__(self):
            return Interpreter.Thunk(-1 * self.get_val().value, self.interpreter, self.scopes, True)
        
        def logical_and(self, other):
            return Interpreter.Thunk(self.get_val().value and other.get_val().value, self.interpreter, self.scopes, True)
        
        def logical_or(self, other):
            return Interpreter.Thunk(self.get_val().value or other.get_val().value, self.interpreter, self.scopes, True)
        
        def logical_not(self):
            return Interpreter.Thunk(not self.get_val().value, self.interpreter, self.scopes, True)

    def get_main_func_node(self, ast):
        if ast.elem_type == self.PROGRAM_NODE:
            for f in ast.dict['functions']:
                func_name = f.dict['name'] + '_' + str(len(f.dict['args']))
                self.func_defs_to_node[func_name] = f
        if 'main_0' in self.func_defs_to_node:
            return self.func_defs_to_node['main_0']
        super().error(
            ErrorType.NAME_ERROR,
            "No main() function was found"
        )

    def run(self, program):
        self.ast = parse_program(program)
        if self.trace_output:
            print(self.ast)
        self.var_name_to_val = dict()
        self.func_defs_to_node = dict()
        self.global_scope = [ self.var_name_to_val ]
        self.val_types = [ self.INT_NODE, self.BOOL_NODE, self.STRING_NODE, self.NIL_NODE ]
        self.arithmetic_ops = ['+', '-', '*', '/', self.NEG_NODE]
        self.comparison_ops = ['<', '>', '<=', '>=', '==', '!=']
        self.bool_ops = ['&&', '||', '!']
        main_func_node = self.get_main_func_node(self.ast)
        self.run_func(main_func_node, self.global_scope)
    
    def run_func(self, func_node, scopes):
        if self.trace_output:
            print("Running function: " + func_node.dict['name'])
            print(scopes)
        for statement in func_node.dict['statements']:
            ret = self.run_statement(statement, scopes)
            if ret or statement.elem_type == self.RETURN_NODE:
                return
        return
    
    def run_statement(self, statement_node, scopes):
        if self.trace_output:
            print('Running statement: ' + statement_node.elem_type)
            print(scopes)
        elem_type = statement_node.elem_type
        ret = self.Thunk(False, self, scopes, True)
        if elem_type == self.VAR_DEF_NODE:
            self.do_definition(statement_node, scopes)
        elif elem_type == '=':
            self.do_assignment(statement_node, scopes)
        elif elem_type == self.FCALL_NODE:
            self.do_call(statement_node, scopes)
        elif elem_type == self.IF_NODE:
            ret = self.do_if(statement_node, scopes)
        elif elem_type == self.FOR_NODE:
            ret = self.do_for(statement_node, scopes)
        elif elem_type == self.RETURN_NODE:
            ret = self.do_return(statement_node, scopes)
        return ret
    
    def run_body(self, statements, scopes):
        if statements == None:
            return self.Thunk(False, self, scopes, True)
        for statement in statements:
            ret = self.run_statement(statement, scopes)
            if ret or statement.elem_type == self.RETURN_NODE:
                return self.Thunk(True, self, scopes, True)
        return self.Thunk(False, self, scopes, True)

    #####################################################################
    # statement behaviors
    #####################################################################
    
    def do_definition(self, statement_node, scopes):
        if self.trace_output:
            print("Running definition: " + statement_node.dict['name'])
            print(scopes)
        local_scope = scopes[-1]
        var_name = statement_node.dict['name']
        if var_name in local_scope:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} defined more than once",
            )
        local_scope[statement_node.dict['name']] = self.Thunk(None, self, scopes, True)
        return
    
    def do_assignment(self, statement_node, scopes):
        if self.trace_output:
            print("Running assignment: " + statement_node.dict['name'])
            print(scopes)
        ref_scope = None
        var_name = statement_node.dict['name']
        for scope in reversed(scopes):
            if var_name in scope:
                ref_scope = scope
                break
        if ref_scope == None:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )

        expression = statement_node.dict['expression']
        result = self.Thunk(None, self, scopes, True)
        if expression.elem_type in self.val_types:
            result = self.evaluate_value(expression, scopes)
        elif expression.elem_type == self.VAR_NODE:
            result = self.Thunk(expression, self, scopes, False)
        elif expression.elem_type == self.NIL_NODE:
            result = self.Thunk(None, self, scopes, True)
        elif expression.elem_type in self.arithmetic_ops or expression.elem_type in self.bool_ops or expression.elem_type in self.comparison_ops: #expression
            result = self.Thunk(expression, self, scopes, False)
        else: # FCALL
            result = self.Thunk(expression, self, scopes, False)

        ref_scope[var_name] = copy.deepcopy(result)
        return
    
    def do_call(self, statement_node, scopes):
        if self.trace_output:
            print('Running call: ' + statement_node.dict['name'])
            print(scopes)
        fcall_name = statement_node.dict['name']

        if fcall_name == 'print':
            self.fcall_print(statement_node.dict['args'], scopes)
            return
        elif fcall_name == 'inputi':
            return self.fcall_inputi(scopes, statement_node.dict['args'])
        elif fcall_name == 'inputs':
            return self.fcall_inputs(scopes, statement_node.dict['args'])
        
        
        fcall_dict_key = fcall_name + '_' + str(len(statement_node.dict['args']))
        if fcall_dict_key not in self.func_defs_to_node:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {fcall_name} was not found",
            )
        func_context = self.prepare_func_context(statement_node, fcall_dict_key, scopes)

        self.run_func(self.func_defs_to_node[fcall_dict_key], func_context)
        return func_context[0]['ret'], func_context
    
    def prepare_func_context(self, func_node, dict_key, scopes):
        fcall_arg_name_list = self.func_defs_to_node[dict_key].dict['args']
        fcall_arg_list = func_node.dict['args']
        new_scope = dict()
        new_scope['ret'] = None
        for i in range(len(fcall_arg_list)):
            cur_arg_node = fcall_arg_list[i]
            arg = self.Thunk(None, self, scopes, True)
            if cur_arg_node.elem_type == self.VAR_NODE:
                arg = self.get_variable_node(cur_arg_node, scopes)
            elif cur_arg_node.elem_type in self.val_types:
                arg = self.evaluate_value(cur_arg_node, scopes)
            elif cur_arg_node.elem_type == self.FCALL_NODE:
                arg = self.Thunk(cur_arg_node, self, scopes, False)
            else: # expression
                arg = self.Thunk(cur_arg_node, self, scopes, False)
            new_scope[fcall_arg_name_list[i].dict['name']] = arg

        func_context = [new_scope, dict()]
        return func_context
    
    def do_if(self, if_node, scopes):
        if self.trace_output:
            print("Running if node")
            print(scopes)
        condition_result = self.Thunk(None, self, scopes, True)
        condition_node = if_node.dict['condition']
        condition_result = self.evaluate_conditional(condition_node, scopes)
        new_scopes = scopes + [dict()]
        if condition_result: 
            ret = self.run_body(if_node.dict['statements'], new_scopes)
        else:
            ret = self.run_body(if_node.dict['else_statements'], new_scopes)

        if ret:
            return self.Thunk(True, self, scopes, True)
        return self.Thunk(False, self, scopes, True)
    
    def do_for(self, for_node, scopes):
        if self.trace_output:
            print("Running for_loop")
            print(scopes)
        self.do_assignment(for_node.dict['init'], scopes)
        condition_node = for_node.dict['condition']
        condition_eval = self.evaluate_conditional(condition_node, scopes)
        while condition_eval:
            new_scope = scopes + [dict()]
            ret = self.run_body(for_node.dict['statements'], new_scope)
            if ret:
                return self.Thunk(True, self, scopes, True)
            self.do_assignment(for_node.dict['update'], scopes)
            condition_eval = self.evaluate_conditional(condition_node, scopes)
        return self.Thunk(False, self, scopes, True)
    
    def do_return(self, return_node, scopes):
        if self.trace_output:
            print("Running return")
            print(scopes)
        ret_val = self.Thunk(None, self, scopes, True)
        if return_node.dict['expression'] == None:
            return self.Thunk(True, self, scopes, True)
        
        ret_eval_type = return_node.dict['expression'].elem_type
        if ret_eval_type == self.VAR_NODE:
            ret_val = self.get_variable_node(return_node.dict['expression'], scopes)
        elif ret_eval_type in self.val_types:
            ret_val = self.evaluate_value(return_node.dict['expression'], scopes)
        elif ret_eval_type == self.FCALL_NODE or ret_eval_type in self.bool_ops or ret_eval_type in self.arithmetic_ops or ret_eval_type in self.comparison_ops:
            ret_val = self.Thunk(return_node.dict['expression'], self, scopes, False)
        scopes[0]['ret'] = ret_val
        return self.Thunk(True, self, scopes, True)

    #####################################################################
    # expression node evaluation 
    #####################################################################
    
    def evaluate_expression(self, expression_node, scopes):
        if self.trace_output:
            print("Running evaluation: " + expression_node.elem_type)
            print(scopes)
        elem_type = expression_node.elem_type
        elem_1 = expression_node.dict['op1']
        operand_1 = self.evaluate_operand(elem_1, scopes).get_val()

        if elem_type == self.NEG_NODE:
            if operand_1.get_type() is not int:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible type for neg operation"
                )
            return -operand_1
        elif elem_type == self.NOT_NODE:
            if operand_1.get_type() is not bool:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible type for ! operation"
                )
            return operand_1.logical_not()
        
        elem_2 = expression_node.dict['op2']
        operand_2 = self.evaluate_operand(elem_2, scopes).get_val()

        if elem_type == '+':
            if operand_1.get_type() is operand_2.get_type() and operand_1.get_type() is not bool:
                return operand_1 + operand_2
            super().error(
                ErrorType.TYPE_ERROR,
                f"Cannot use operator + on boolean or mismatched operators"
            )
        elif elem_type == '-':
            if operand_1.get_type() is not int or operand_2.get_type() is not int:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Cannot use operator - on non-integer operators"
                )
            return operand_1 - operand_2
        elif elem_type == '/':
            if operand_1.get_type() is not int or operand_2.get_type() is not int:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Cannot use operator / on non-integer operators"
                )
            return int(operand_1 // operand_2)
        elif elem_type == '*':
            self.type_check(operand_1, operand_2, elem_type)
            self.verify_integer(operand_1, elem_type)
            return operand_1 * operand_2
        elif elem_type == '==':
            if operand_1.get_type() is not operand_2.get_type():
                return False
            return operand_1 == operand_2
        elif elem_type == '<':
            self.type_check(operand_1, operand_2, elem_type)
            self.verify_integer(operand_1, elem_type)
            return operand_1 < operand_2
        elif elem_type == '>':
            self.type_check(operand_1, operand_2, elem_type)
            self.verify_integer(operand_1, elem_type)
            return operand_1 > operand_2
        elif elem_type == '<=':
            self.type_check(operand_1, operand_2, elem_type)
            self.verify_integer(operand_1, elem_type)
            return operand_1 <= operand_2
        elif elem_type == '>=':
            self.type_check(operand_1, operand_2, elem_type)
            self.verify_integer(operand_1, elem_type)
            return operand_1 >= operand_2
        elif elem_type == '!=':
            if operand_1.get_type() is not operand_2.get_type():
                return True
            return operand_1 != operand_2
        elif elem_type == '||':
            if operand_1.get_type() is not bool or operand_2.get_type() is not bool:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Cannot use operator || on non-boolean operators"
                )
            return operand_1.logical_or(operand_2)
        elif elem_type == '&&':
            if operand_1.get_type() is not bool or operand_2.get_type() is not bool:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Cannot use operator && on non-boolean operators"
                )
            return operand_1.logical_and(operand_2)

    #####################################################################
    # variable node evaluation 
    #####################################################################
    
    def evaluate_variable_node(self, var_node, scopes):
        if self.trace_output:
            print("Running retrieval: " + var_node.dict['name'])
            print(scopes)
        var_name = var_node.dict['name']
        for scope in reversed(scopes):
            if var_name in scope:
                return scope[var_name].get_val()
        super().error(
            ErrorType.NAME_ERROR,
            f"Variable {var_name} has not been defined",
        )

    def get_variable_node(self, var_node, scopes):
        if self.trace_output:
            print("Running lazy retrieval: " + var_node.dict['name'])
            print(scopes)
        var_name = var_node.dict['name']
        for scope in reversed(scopes):
            if var_name in scope:
                return scope[var_name]
        super().error(
            ErrorType.NAME_ERROR,
            f"Variable {var_name} has not been defined",
        )

    #####################################################################
    # value node evaluation 
    #####################################################################
    
    def evaluate_value(self, val_node, scopes):
        if self.trace_output:
            print("Running constant_type: " + val_node.elem_type)
            print(scopes)
        if val_node.elem_type == self.BOOL_NODE:
            if val_node.dict['val'] == self.TRUE_DEF:
                return self.Thunk(True, self, scopes, True)
            elif val_node.dict['val'] == self.FALSE_DEF:
                return self.Thunk(False, self, scopes, True)
        elif val_node.elem_type == self.NIL_NODE:
            return self.Thunk(None, self, scopes, True)
        return self.Thunk(val_node.dict['val'], self, scopes, True)

    #####################################################################
    # operand node evaluation 
    #####################################################################
    
    def evaluate_operand(self, operand_node, scopes):
        if operand_node.elem_type == self.VAR_NODE:
            return self.evaluate_variable_node(operand_node, scopes)
        elif operand_node.elem_type in self.arithmetic_ops or operand_node.elem_type in self.bool_ops or operand_node.elem_type in self.comparison_ops:
            return self.evaluate_expression(operand_node, scopes)
        elif operand_node.elem_type == self.FCALL_NODE:
            return self.do_call(operand_node, scopes)[0]
        elif operand_node.elem_type == self.NIL_NODE:
            return self.Thunk(None, self, scopes, True)
        else:
            return self.evaluate_value(operand_node, scopes)


    #####################################################################
    # conditional (for/if) node evalution
    #####################################################################
    
    def evaluate_conditional(self, condition_node, scopes):
        condition_type = condition_node.elem_type
        condition_eval = self.Thunk(None, self, scopes, True)
        if condition_type == self.VAR_NODE:
            condition_eval = self.evaluate_variable_node(condition_node, scopes)
        elif condition_type == self.BOOL_NODE:
            condition_eval = self.evaluate_value(condition_node, scopes)
        elif condition_type in self.bool_ops or condition_type in self.comparison_ops:
            condition_eval = self.evaluate_expression(condition_node, scopes)

        if not self.check_boolean(condition_eval):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Expression does not evaluate to boolean",
            )
        return condition_eval

    #####################################################################
    # custom functions (called from any scope)
    #####################################################################

    def fcall_print(self, args, scopes):
        if self.trace_output:
            print("Running print")
            print(scopes)
        output = ""
        for arg in args:
            if arg.elem_type == self.VAR_NODE:
                res = self.evaluate_variable_node(arg, scopes)
                if res.get_type() is bool:
                    output += self.fcall_print_bool_helper(res)
                else:
                    output += str(res.get_val().value)
            elif arg.elem_type == self.INT_NODE or arg.elem_type == self.STRING_NODE:
                output += str(self.evaluate_value(arg, scopes).get_val().value)
            elif arg.elem_type in self.arithmetic_ops:
                output += str(self.evaluate_expression(arg, scopes).get_val().value)
            elif arg.elem_type in self.comparison_ops or arg.elem_type in self.bool_ops:
                res = self.evaluate_expression(arg, scopes)
                output += self.fcall_print_bool_helper(res)
            elif arg.elem_type == self.BOOL_NODE:
                output += self.fcall_print_bool_helper(arg.dict['val'])
            elif arg.elem_type == self.FCALL_NODE:
                res = self.do_call(arg, scopes)[0]
                if res.get_type() is bool:
                    output += self.fcall_print_bool_helper(res)
                else:
                    output += str(res.get_val().value)
        super().output(output)
        print("OUTING")
        print(scopes)
        return self.Thunk(None, self, scopes, True)
    
    def fcall_inputi(self, scopes, prompt = None):
        if self.trace_output:
            print("Running inputi")
        if prompt is None:
            prompt = ""
        elif len(prompt) > 2:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",
            )
        elif len(prompt) > 0:
            super().output(self.evaluate_value(prompt[0], scopes))
        return self.Thunk(int(super().get_input()), self, scopes, True)

    def fcall_inputs(self, scopes, prompt = None):
        if self.trace_output:
            print("Running inputs")
        if prompt is None:
            prompt = ""
        elif len(prompt) > 2:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputs() function found that takes > 1 parameter",
            )
        elif len(prompt) > 0:
            super().output(self.evaluate_value(prompt[0], scopes))
        return self.Thunk(str(super().get_input()), self, scopes, True)


    #####################################################################
    #  Util and Abstracted helpers
    #####################################################################
    def check_boolean(self, condition):
        return condition.get_type() is bool

    def fcall_print_bool_helper(self, val):
        if val:
            return 'true'
        return 'false'

    def verify_integer(self, condition, elem_type):
        if condition.get_type() is not int:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {elem_type} operation",
            )

    def type_check(self, op_1, op_2, elem_type):
        if op_1.get_type() is not op_2.get_type():
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {elem_type} operation",
            )

    
    
