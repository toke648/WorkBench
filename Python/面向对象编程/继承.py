# from Python.面向对象编程.面向对象Class类 import student
#
# # 面向对象
# # 封装、继承、动态
#
# # 没有继承的类
# class kid(student):
#     age = 6
#
#     def homework(self):
#         # make simple homework
#         pass
#
# class youth(student):
#     age = 18
#
#     def homework(self):
#         # make difficulty homework
#         pass
#
# # 继承后的类，功能更加简洁美观，便于理解
# # __init__，初始自定义变量，用于继承方法
#
# class Student:
#     #
#     def __init__(self, age, num, grade):
#         self.age = age
#         self.number = num
#         self.grades = grade
#
#     def go_school(self, school):
#         pass
#
# Jhon = kid('08', 'first school')
# Anny = youth('24', 'University')
#
# my_kid = [Jhon, Anny]
#
# for i in my_kid:
#     print(i)


class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id
        self.grades = {'China': 0,'Math': 0,'English': 0}

    def set_grade(self, course, grade):
        if course in self.grades:
            self.grades[course] = grade

    def print_grades(self):
        print(f'student:{self.name} (student_id:{self.student_id}) 的成绩为：')
        for course in self.grades:
            print(f'{course}: {self.grades[course]}分')

chen = Student('Mr chen', '100618')
zeng = Student('Mr zeng', '100622')
print(chen.name)
zeng.set_grade('Math', 95)
print(zeng.grades)

chen.set_grade('China', 92)
chen.set_grade('English', 62)
chen.print_grades()
zeng.set_grade('China', 92)
zeng.set_grade('English', 62)
zeng.print_grades()



# 类的继承和分类
# 子类及父类

# 父类
class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    def print_info(self):
        print(f'Employee:{self.name}, employee_id:{self.employee_id}')

# 子类
class FullTimeEmployee(Employee):
    def __init__(self, name, employee, monthly_salary):
        # 子类特定属性
        super().__init__(name, employee)
        self.monthly_salary = monthly_salary

    def calculate_monthly_pay(self):
        return self.monthly_salary


# 子类
class PartTimeEmployee(Employee):
    def __init__(self, name, employee, daily_salary, work_days):
        # 子类特定属性
        super().__init__(name, employee)
        self.daily_salary = daily_salary
        self.work_days = work_days

    def calculate_monthly_pay(self):
        return self.daily_salary * self.work_days

chen = FullTimeEmployee('Mr chen', '100618', 6000)
zeng = PartTimeEmployee('Mr zeng', '100622', 300, 13)
chen.print_info()
zeng.print_info()
print(chen.calculate_monthly_pay())
print(zeng.calculate_monthly_pay())


with open('E:\\Tim\\File\\AI\\项目\\AI人机交互模型\\通义千问（大型语言模型）\\AI\\Text-to-speech(TTS)\\wenzi.txt') as f:
    print(f.read())
    f.close()

try:
    user_weight = float('dfdsa')
    user_height = float('input('')')
    user_BMI = user_weight / user_height ** 2
except ValueError:
    print('输入为不合理数字，请重新运行程序，并输入正确数字。')
except ZeroDivisionError:
    print('身高不能为零，请重新运行程序，并输入正确的数字。')
except:
    print('发生了未知错误，请重新运行程序。')
else:
    print('')
finally:
    print('程序运行结束。')
