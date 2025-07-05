"""
data_structures.py

Examples of using Python data structures professionally.
"""

from typing import Dict, List


class Student:
    """Class representing a student with name and grades."""

    def __init__(self, name: str, grades: List[float]) -> None:
        self.name = name
        self.grades = grades

    def average_grade(self) -> float:
        """Calculate and return the average grade."""
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)

    def __repr__(self) -> str:
        return f"Student(name={self.name!r}, grades={self.grades!r})"


def get_top_student(students: List[Student]) -> Student:
    """Return the student with the highest average grade."""
    return max(students, key=lambda student: student.average_grade())


if __name__ == "__main__":
    students_list = [
        Student("Alice", [85.0, 92.5, 78.0]),
        Student("Bob", [90.0, 88.0, 91.0]),
        Student("Charlie", [70.0, 75.5, 80.0]),
    ]

    top_student = get_top_student(students_list)
    print(f"Top student: {top_student.name} with average grade {top_student.average_grade():.2f}")
