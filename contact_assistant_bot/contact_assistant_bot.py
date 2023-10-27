from datetime import datetime, timedelta
import calendar
from collections import defaultdict
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        if not (len(phone) == 10 and phone.isdigit()):
            raise ValueError("Phone number must be 10 digits long")
        
        super().__init__(phone)


class Birthday(Field):
    def __init__(self, birthday):
        try:
            date = datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Birthday must be in the format DD.MM.YYYY")
        
        super().__init__(date)
    

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone_number):
        '''
        Додавання телефонів
        '''
        phone = Phone(phone_number)
        self.phones.append(phone)

    def edit_phone(self, old_number, new_number):
        '''
        Редагування телефонів
        '''
        phone = self.find_phone(old_number)
        if phone:
            phone.value = new_number
            return True
        return False

    def find_phone(self, phone_number):
        '''
        Пошук телефону
        '''
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        '''
        Додавання записів
        '''
        if isinstance(record, Record):
            self.data[record.name.value] = record

    def find(self, name):
        '''
        Пошук записів за іменем
        '''
        return self.data.get(name)

    def delete(self, name):
        '''
        Видалення записів за іменем
        '''
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        '''
        Дні народження на наступному тижні
        '''
        today = datetime.today().date()
        week_ahead = today + timedelta(days=7)
        birthdays = defaultdict(list)

        for name, record in self.data.items():
            if record.birthday:  # день народження
                birthday_date = record.birthday.value.date()  # отримуємо об'єкт date

                # Створюємо об'єкт datetime дня народження цього року
                birthday_this_year = birthday_date.replace(year=today.year)

                # Якщо день народження вже був цього року, тоді перевіряємо наступний рік
                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)

                # Чи день народження наступного тижня
                if today <= birthday_this_year <= week_ahead:
                    day_of_week = birthday_this_year.weekday()
                    day_name = calendar.day_name[day_of_week]

                    # Якщо припадає на вихідні, тоді переносимо на понеділок
                    if day_of_week in [5, 6]:
                        day_name = 'Monday'

                    birthdays[day_name].append(record.name.value)
        
        return birthdays
    

def input_error(func):
    '''
    Обробка винятків
    '''
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if str(e) in ["Phone number must be 10 digits long", "Birthday must be in the format DD.MM.YYYY"]:
                return str(e)
            else:
                return "Give me correct data please"
        except IndexError:
            return "Missing arguments"
        except KeyError:
            return "Not found"
    return inner

@input_error
def add_contact(args, book):
    '''
    Додає новий контакт до словника контактів
    '''
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)

    return "Contact added."

@input_error
def change_contact(args, book):
    '''
    Оновлює номер телефону існуючого контакту
    '''
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return f"Contact updated."
    else:
        return "Not found."

@input_error
def show_phone(args, book):
    '''
    Відображає номер телефону контакту
    '''
    [name] = args
    record = book.find(name)
    if record:
        return ', '.join(map(str, record.phones))
    else:
        return f"Not found."

@input_error
def show_all(book):
    '''
    Відображає всі збережені контакти
    '''
    if not book.data:
        return "No contacts stored."

    return '\n'.join([f"{record.name}: {', '.join(map(str, record.phones))}" for record in book.data.values()])
    
@input_error
def add_birthday(args, book):
    '''
    Додає дату дня народження до контакту
    '''
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    '''
    Відображає дату дня народження по контакту
    '''
    [name] = args
    record = book.find(name)
    if record and record.birthday:
        return str(record.birthday)
    else:
        return "No birthday found for this contact."

@input_error
def show_birthdays_next_week(book):
    '''
    Відображає дні народження на наступному тижні
    '''
    birthdays_next_week = book.get_birthdays_per_week()
    if not birthdays_next_week:
        return "No birthdays next week."

    response = []
    for day, names in birthdays_next_week.items():
        response.append(f"{day}: {', '.join(names)}")

    return "\n".join(response)

def hello_command():
    return "How can I help you?"
    
def parse_input(user_input):
    '''
    Обробляє введені дані, розділяючи рядок на команду та аргументи
    '''
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    '''
    Головна функція, де знаходиться логіка бота
    '''
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")  # Отримання команди від користувача
        command, *args = parse_input(user_input)  # Парсинг команди

        # Перевірка команд та відповідна дія
        if command == "hello":
            print(hello_command())
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(show_birthdays_next_week(book))
        elif command in ["close", "exit"]:
            print("Good bye!")
            break  # Вихід
        else:
            print(f"Command '{command}' not recognized")

# Точка входу
if __name__ == "__main__":
    main()