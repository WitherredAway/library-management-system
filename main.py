import datetime


FINE_PER_DAY = 10  # Fine amount per day in rupees
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

    # This list comprehension is used to format each key and value of the dictionary
    return "\n".join(
        [
            f"{indent}{key.title() if isinstance(key, str) else key}: {value}"
            for key, value in dictionary.items()
        ]
    )


def format_books_dict(book_dict, *, indent=""):
    """Function to nicely format a book dictionary"""

    # This list comprehension is used to format each key and value of the book dictionary
    return "\n\n".join(
        [
            f"{indent}ID: {book_id}\n{format_dict(book, indent=indent)}"
            for book_id, book in book_dict.items()
        ]
    )


def input_member():
    """Function to get member from member ID input"""

    member_id = int(input("Please input the member's ID: "))
    print()
    member = members.get(member_id)
    return member_id, member


def input_book():
    """Function to get book from book ID input"""

    book_id = int(input("Please input the book's ID: "))
    print()
    book = books.get(book_id)
    return book_id, book


# The main data
members = {1: {"name": "Souvic Das", "member since": str_to_date(), "issued books": []}}
books = {
    1: {
        "name": "Sherlock Holmes Vol. 1",
        "author": "Arthur Conan Doyle",
        "published year": 1887,
    }
}

# Dictionary of issued books. It is a dictionary whose
# each key is a member ID and value is a dictionary whose
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
while True:
    # This try-except block catches ValueError in case a string was input
    try:
        option = int(
            input(
                f"""
1. View Member Details
2. View Book Details
3. View Inventory
4. View Issued Books

5. Add a Member
6. Add a Book
7. Issue a Book

8. Exit
Please select an option (1-8): """
            )
        )
    except ValueError:
        print("Please select an integer option from 1 to 8")
        continue

    # This print statement is to add an extra line after the menu
    print()

    # If selected action is not within list of options
    if not 1 <= option <= 8:
        print("Selected option is out of range")
        continue
    # If selected option is 1: View Member Details
    if option == 1:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        member_issued_books = issued_books.get(member_id)
        if member_issued_books is not None:
            # Update list of issued book IDs of the member
            member["issued books"].extend(member_issued_books.keys())

        print(format_dict(member))
    # If selected option is 2: View Book Details
    elif option == 2:
        book_id, book = input_book()
        if book is None:
            print(f"Book with ID {book_id} does not exist.")
            continue
        print(format_dict(book))
    # If selected option is 3: View inventory
    elif option == 3:
        print(
            "Books currently in inventory:\n" + format_books_dict(books, indent="    ")
        )
    # If selected option is 4: View Issued Books
    elif option == 4:
        member_id, member = input_member()
        if member is None:
            print(f"Member with ID {member_id} does not exist.")
            continue

        issues = issued_books.get(member_id)
        if issues is None or len(issues) == 0:
            print(
                f"Member {member['name']} (#{member_id}) does not have any issued books."
            )
            continue

        for book_id, issue in issues.items():
            today = str_to_date()
            issued_until = issue["issued until"]
            # If today is greater than expiry date aka expiry date has passed
            if today > issued_until:
                # Update fine amount based on fine per day
                issues[book_id]["fine amount"] = (today - issued_until).days * FINE_PER_DAY
            # Else, if there is fine amount assigned but they're no longer eligible for it, remove it
            elif "fine amount" in issues[book_id]:
                del issues[book_id]["fine amount"]

        msg = format_books_dict(issues, indent="    ")

        print(
            f"Books issued to {members[member_id]['name']} (#{member_id}):\n"
            + "".join(msg),
        )
    # If selected option is 5: Add a member
    elif option == 5:
        name = input("Please input name of the member: ").title()
        member_id = max(members.keys()) + 1  # Determine next member ID

        members[member_id] = {
            "name": name,
            "member since": str_to_date(),
            "issued books": [],
        }
        print(f"Added new member {name} (#{member_id})")
    # If selected option is 6: Add a book
    elif option == 6:
        name = input("Please input name of the book: ")
        author = input("Please input author of the book: ").title()
        year = int(input("Please input publication year of the book: "))
        book_id = max(books.keys()) + 1  # Determine next book ID

        books[book_id] = {
            "name": name,
            "author": author,
            "published year": year,
        }
        print(f"Added new book {name} (#{book_id})")
    # If selected option is 7: Issue a book
    elif option == 7:
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
        # If expiry date is less than today; issue has expired
        elif issued_book["issued until"] < str_to_date():
            renew = input("Renew issuance? y/N: ")
            if renew not in "yY":
                print("Aborted")
                continue
            issued_book["issued date"] = str_to_date()
            issued_book["issued until"] = str_to_date() + datetime.timedelta(
                days=REINSTATEMENT_DAYS
            )
        # Else, i.e. when expiry date is larger than today; issue hasn't expired yet
        else:
            remaining = (
                issued_book["issued until"] - str_to_date()
            ).days  # Difference (in days) between expiration date and today
            print(
                # This string is split into two halves to reduce the no. of characters in the line
                (
                    f"Book {book['name']} (#{book_id}) is already issued"
                    f" to {member['name']} (#{member_id}) for {remaining} more days"
                )
            )
            renew = input(
                f"Increase issuance period by {REINSTATEMENT_DAYS} days? y/N: "
            )
            if renew not in "yY":
                print("Aborted")
                continue

            issued_book["issued until"] = issued_book[
                "issued until"
            ] + datetime.timedelta(days=REINSTATEMENT_DAYS)
        print(
            # This string is split into two halves to reduce the no. of characters in the line
            (
                f"Issued book {book['name']} (#{book_id})"
                f" to {member['name']} (#{member_id}) for + {REINSTATEMENT_DAYS} days"
            )
        )
    # If selected option is 8: Exit, break out of the loop
    elif option == 8:
        break
