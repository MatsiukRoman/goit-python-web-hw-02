from collections import UserDict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import pickle

class DataRepository(ABC):
    @abstractmethod
    def save_data(self, data, filename):
        pass
    
    @abstractmethod
    def load_data(self, filename):
        pass

class AddressBookDataRepository(DataRepository):
    def save_data(self, data, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook() 


class CheckPhoneNumber(Exception):
    pass

class Field(ABC):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit():
           raise CheckPhoneNumber(f'Phone {value} is not digit') 
        elif len(value) != 10:
            raise CheckPhoneNumber(f'Phone {value} > 10 digits')
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class RecordBase(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def add_phone(self, phone):
        pass

    @abstractmethod
    def remove_phone(self, phone):
        pass

    @abstractmethod
    def remove_all_phones(self):
        pass

    @abstractmethod
    def edit_phone(self, old_phone, new_phone):
        pass

    @abstractmethod
    def find_phone(self, phone):
        pass

    @abstractmethod
    def add_birthday(self, birthday_date):
        pass


class Record(RecordBase):
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'N/A'}"
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    
    def remove_all_phones(self):
        self.phones = []

    def edit_phone(self, old_phone, new_phone):
        try:
            new_phone_obj = Phone(new_phone)  
        except CheckPhoneNumber as e:
            return str(e)
        
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone_obj.value

    def find_phone(self, phone):
        try:
            found_phone = next(item for item in self.phones if item.value == phone)
            return found_phone
        except StopIteration:
            return None
        
    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)

class RecordManager(ABC):
    @abstractmethod
    def add_record(self, record):
        pass

    @abstractmethod
    def find(self, name):
        pass
    
    @abstractmethod
    def delete(self, name):
        pass


class AddressBook(UserDict, RecordManager):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]


class BirthdayManager:
    @staticmethod
    def find_next_weekday(start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    @staticmethod
    def adjust_for_weekend(birthday):
        if birthday.weekday() >= 5:
            return BirthdayManager.find_next_weekday(birthday, 0)
        return birthday

    @staticmethod
    def get_upcoming_birthdays(address_book: RecordManager, days=7):
        print(address_book)
        upcoming_birthdays = []
        today = datetime.today()
        for name, record in address_book.data.items():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = record.birthday.value.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    birthday_this_year = BirthdayManager.adjust_for_weekend(birthday_this_year)
                    upcoming_birthdays.append({"Contact": name, "upcoming birthday": birthday_this_year.strftime("%d.%m.%Y")})
        return upcoming_birthdays
  
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Incorrect value."
        except KeyError:
            return "Enter the argument for the command"
        except IndexError:
            return "Enter the argument for the command"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
    
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact changed."
    if record is None:
        message = "Contact not found."
    else:
        record.remove_all_phones() # clean all phones
        record.add_phone(phone)
    return message

@input_error
def get_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact not found!"
    else:
        return f"{record}"
    
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_date, *_ = args
    record = book.find(name)
    message = "Contact birthday updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added. Birthday updated."
    if birthday_date:
        record.add_birthday(birthday_date)
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact not found!"
    else:
        if not record.birthday is None:
            return f"{record.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return None


def birthdays(book: AddressBook):
    return BirthdayManager.get_upcoming_birthdays(book)

def main():
    address_book_repository = AddressBookDataRepository()
    book = address_book_repository.load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            address_book_repository.save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(get_phone(args, book))

        elif command == "all":
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()