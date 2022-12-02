import datetime


DATETIME_FORMAT = r"%d/%m/%Y"  # Constant for the format for datetime objects
FINE_PER_DAY = 10  # Fine amount per day


# All the utility functions
def str_to_date(date_str=None):
    """This function returns the current date and time in IST timezone"""
    if date_str is None:
        date_obj = datetime.date.today()
    else:
        day, month, year = date_str.split("/")
        date_obj = datetime.date(int(year), int(month), int(day))

    return date_obj


def format_dict(dictionary, *, indent=""):
    """Function to nicely format the keys and values of a dictionary"""

    # This is a list comprehension; creating a list using for loop directly within the brackets
    return "\n" + "\n".join(
        [
            f"{indent}{key.title() if isinstance(key, str) else key}: {value.title() if isinstance(value, str) else value}"
            for key, value in dictionary.items()
        ]
    )


def format_books_dict(book_dict, *, indent=""):
    """Function to nicely format a book dictionary"""

    return "\n" + "\n".join(
        [
            f"{indent}ID: {book_id}{format_dict(book, indent=indent)}"
            for book_id, book in book_dict.items()
        ]
    )


def input_member():
    member_id = int(input("Please input the ID of the member: "))
    member = members.get(member_id)
    return member_id, member


# All the data
members = {
    1: {"name": "Souvic Das", "member since": str_to_date(), "issued books": []}
}
books = {
    1: {
        "name": "Sherlock Holmes Vol. 1",
        "author": "Arthur Conan Doyle",
        "published year": 1887,
    }
}

# Dictionary of issued books. It is a dictionary whose
# each key is a member ID and value is a list of book dictionaries whose
# each key is a book ID and value is the issue details
issued_books = {
    1: {
        1: {
            "issued date": str_to_date("01/10/2022"),
            "issued until": str_to_date("01/11/2022"),
        }
    }
}


# The main loop of the program
run = True
while run:
    action = int(
        input(
            f"""
1. View Member Details
2. View Book Details
3. View Inventory
4. View Issued Books

5. Add Member
6. Add Book
7. Issue a book

8. Exit
Please select an option: """
        )
    )
    if not 1 <= action <= 8:
        print("Selected option is out of range")
        continue

    if action == 1:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        member_issued_books = issued_books.get(member_id)
        if member_issued_books is not None:
            member["issued books"].extend(member_issued_books.keys())

        print(format_dict(member))

    elif action == 2:
        book_id = int(input("Please input the book's ID: "))
        book = books.get(book_id)
        if book is None:
            print(f"Book with ID {book_id} does not exist.")
            continue

        print(format_dict(book))

    elif action == 3:
        print("Books currently in inventory:" + format_books_dict(books, indent="    "))

    elif action == 4:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        issues = issued_books.get(member_id)
        if issues is None or len(issues) == 0:
            print(f"Member with ID {member_id} does not have any issued books.")
            continue
        for book_id, issue in issues.items():
            today = str_to_date()
            issued_until = issue["issued until"]
            if today > issued_until:
                issues[book_id]["fine amount"] = (today - issued_until).days * FINE_PER_DAY  # type: ignore

        msg = format_books_dict(issues, indent="    ")

        print(
            f"Books issued to {members[member_id]['name']} ({member_id}):", "".join(msg)
        )

    elif action == 8:
        break
