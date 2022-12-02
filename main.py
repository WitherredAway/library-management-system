import datetime


FINE_PER_DAY = 10  # Fine amount per day
REINSTATEMENT_DAYS = 28  # No. of days to issue books for


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
    return "\n".join(
        [
            f"{indent}{key.title() if isinstance(key, str) else key}: {value}"
            for key, value in dictionary.items()
        ]
    )


def format_books_dict(book_dict, *, indent=""):
    """Function to nicely format a book dictionary"""

    return "\n\n".join(
        [
            f"{indent}ID: {book_id}\n{format_dict(book, indent=indent)}"
            for book_id, book in book_dict.items()
        ]
    )


def input_member():
    """Function to get member from member ID"""

    member_id = int(input("Please input the member's ID: "))
    print()
    member = members.get(member_id)
    return member_id, member


def input_book():
    """Function to get book from book ID"""

    book_id = int(input("Please input the book's ID: "))
    print()
    book = books.get(book_id)
    return book_id, book


# All the data
members = {1: {"name": "Souvic Das", "member since": str_to_date(), "issued books": []}}
books = {
    1: {
        "name": "Sherlock Holmes Vol. 1",
        "author": "Arthur Conan Doyle",
        "published year": 1887,
    }
}

# Dictionary of issued books. It is a dictionary whose
# each key is a member ID and value is a dictionary
# each key is a book ID and value is the issue details
issued_books = {
    1: {
        1: {
            "issued date": str_to_date("01/11/2022"),
            "issued until": str_to_date("01/12/2022"),
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
    print()
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
        book_id, book = input_book()
        if book is None:
            print(f"Book with ID {book_id} does not exist.")
            continue

        print(format_dict(book))

    elif action == 3:
        print(
            "Books currently in inventory:\n" + format_books_dict(books, indent="    ")
        )

    elif action == 4:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        issues = issued_books.get(member_id)
        if issues is None or len(issues) == 0:
            print(f"Member with #{member_id} does not have any issued books.")
            continue
        for book_id, issue in issues.items():
            today = str_to_date()
            issued_until = issue["issued until"]
            if today > issued_until:
                issues[book_id]["fine amount"] = (today - issued_until).days * FINE_PER_DAY  # type: ignore
            elif "fine amount" in issues[book_id]:
                del issues[book_id]["fine amount"]

        msg = format_books_dict(issues, indent="    ")

        print(
            f"Books issued to {members[member_id]['name']} (#{member_id}):\n"
            + "".join(msg),
        )

    elif action == 5:
        name = input("Please input name of the member: ").title()
        member_id = max(members.keys()) + 1

        members[member_id] = {
            "name": name,
            "member since": str_to_date(),
            "issued books": [],
        }
        print(f"Added new member {name} (#{member_id})")

    elif action == 6:
        name = input("Please input name of the book: ")
        author = input("Please input author of the book: ").title()
        year = int(input("Please input publication year of the book: "))
        book_id = max(books.keys()) + 1

        books[book_id] = {
            "name": name,
            "author": author,
            "published year": year,
        }
        print(f"Added new book {name} (#{book_id})")

    elif action == 7:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        book_id, book = input_book()
        if book is None:
            print(f"Book with ID {book_id} does not exist.")
            continue

        if issued_books.get(member_id) is None:
            issued_books[member_id] = {}

        issued_book = issued_books[member_id].get(book_id)
        if issued_book is None:
            issued_books[member_id][book_id] = {
                "issued date": str_to_date(),
                "issued until": str_to_date()
                + datetime.timedelta(days=REINSTATEMENT_DAYS),
            }
        elif issued_book["issued until"] < str_to_date():
            issued_book["issued date"] = str_to_date()
            issued_book["issued until"] = str_to_date() + datetime.timedelta(
                days=REINSTATEMENT_DAYS
            )
        else:
            remaining = (issued_book["issued until"] - str_to_date()).days
            print(
                f"Book {book['name']} (#{book_id}) is already issued to {member['name']} (#{member_id}) for {remaining} more days"
            )
            renew = input("Renew issuance? y/N: ")
            if renew not in "yY":
                print("Aborted.")
                continue

            issued_book["issued until"] = issued_book[
                "issued until"
            ] + datetime.timedelta(days=REINSTATEMENT_DAYS)

        print(
            f"Issued book {book['name']} (#{book_id}) to {member['name']} (#{member_id}) for + {REINSTATEMENT_DAYS} days"
        )

    elif action == 8:
        break
