import pytest


def test_example():
   assert 1 == 1


def test_in_instane():
   assert  isinstance('toila devbaoo' ,str)
   assert not isinstance('10' ,int)


def test_boolean():
   validated = True
   assert validated is True
   assert ('hello' == 'world') is False


def test_type():
   assert type('hello') is str
   assert type('hello') is not int


def test_greater_and_less_than():
   assert 10 > 5
   assert 10 < 50


def test_list():
   num_list = [1,2,3,4,5]
   any_list = [False, False]
   assert 1 in num_list
   assert 1 not in any_list
   assert all(num_list)
   assert not any(any_list)
   assert any(num_list)


class Student:
   def __init__(self, first_name : str, last_name : str, age : int):
       self.first_name = first_name
       self.last_name = last_name
       self.age = age


@pytest.fixture
def default_student():
   return Student('toila', 'devbaoo', 20)


def test_student(default_student):
   assert default_student.first_name == 'toila'
   assert default_student.last_name == 'devbaoo'
   assert default_student.age == 20
