import datetime

import mysql.connector as mcon


BORDER = "-" * 50
MBORDER = "=" * 50

FINE_PER_DAY = 10  # Fine amount per day in rupees
REINSTATEMENT_DAYS = 28  # No. of days to issue books for


# Make sure to create the 'library' database
con = mcon.connect(host="localhost", user="root", passwd="root", database="library")
# The dictionary kwarg ensures all output is a dictionary of col: value
cursor = con.cursor(dictionary=True)

# Names of the tables
MEMBERS = "members"
BOOKS = "books"
ISSUED_BOOKS = "issued_books"

# Initialize all the required tables
cursor.execute(
    f"""CREATE TABLE IF NOT EXISTS {MEMBERS} (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name TEXT,
        member_since DATE
    )"""
)

cursor.execute(
    f"""CREATE TABLE IF NOT EXISTS {BOOKS} (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name TEXT,
        author TEXT,
        year INTEGER
    )"""
)

cursor.execute(
    f"""CREATE TABLE IF NOT EXISTS {ISSUED_BOOKS} (
        issue_id INT PRIMARY KEY AUTO_INCREMENT,
        member_id INT,
        book_id INT,
        issue_date DATE,
        issue_until DATE,

        FOREIGN KEY (member_id)
            REFERENCES {MEMBERS}(id)
            ON DELETE CASCADE,
        FOREIGN KEY (book_id)
            REFERENCES {BOOKS}(id)
            ON DELETE CASCADE
    )"""
)

con.commit()


# Formatting functions
def border(string):
    """Puts border in lines before and after a string"""
    return f"{BORDER}\n{string}\n{BORDER}"

def date(date=None):
    """This function returns the current date and time in IST timezone"""
    if date is None:
        return datetime.date.today()
    elif isinstance(date, str):
        day, month, year = date.split("/")
        return datetime.date(int(year), int(month), int(day))
    elif isinstance(date, datetime.date):
        return f"{date:%d-%m-%Y}"

    # If it's an unexpected input
    raise ValueError("Invalid input type")

def pretty_dict(dictionary, *, indent=""):
    """Function to nicely format the keys and values of a dictionary"""

    # This list comprehension is used to format each key and value of the dictionary
    details = "\n".join(
        [
            f"{indent}{key}: {value}"
            for key, value in dictionary.items()
        ]
    )
    return details

def format_book(book):
    try:
        return {
            "Book ID": book["id"],
            "Name": book["name"],
            "Author": book["author"],
            "Release Year": book["year"]
        }
    except KeyError:
        return book

def format_books(books, *, indent=""):
    """Function to nicely format a list of book dictionaries"""

    # This list comprehension is used to format each key and value of the book dictionary
    books_list = []
    for book in books:
        books_list.append(format_book(book))

    return "\n\n".join(
        [
            pretty_dict(book, indent=indent)
            for book in books_list
        ]
    )

def tabulate(data):
    """Function to nicely tabulate data

    'data' has to be a list of dictionaries.
    Each of those dictionaries need to have the same keys,
    which will be the columns. E.g.:
    [
        {'id': 1, 'name': 'Souvic Das', 'member_since': datetime.date(2023, 7, 20)},
        {'id': 2, 'name': 'Arkaprovo Das', 'member_since': datetime.date(2023, 7, 21)},
        {'id': 3, 'name': 'Sukrit Dutta', 'member_since': datetime.date(2023, 7, 21)},
        {'id': 4, 'name': 'Shibam Dutta', 'member_since': datetime.date(2023, 7, 21)},
    ]
    """

    if len(data) == 0:
        return ""

    # Ensure that all rows are of the same length
    if not all(len(d) == len(data[0]) for d in data):
        raise ValueError("Inconsistent row lengths")

    # Ensure that all rows have the same headers
    if not all(all(data[0].get(k) is not None for k in d) for d in data):
        raise ValueError("Inconsistent headers")

    # Dictionary of each header and its largest value
    headers = {k: max([len(str(d[k])) for d in data] + [len(k)]) for k in data[0].keys()}
    data_list = []

    # Loop through each row and put each value into a tuple
    for row in data:
        d = []
        for h in headers:
            v = row[h]
            # If a value is a date object, turn it into string
            if isinstance(v, datetime.date):
                v = date(v)
            d.append(v)
        data_list.append(d)

    # Use Format Mini Lang to create the padding for each cell
    row_format = "| " + " | ".join(["{:<%s}" % hl for _, hl in headers.items()]) + " |"
    # And the horizontal border
    border = "+-" + "-+-".join([f"{'':-<{hl}}" for _, hl in headers.items()]) + "-+"

    # Finally, build the table
    table = []
    table.append(border)
    table.append(row_format.format(*headers))
    table.append(border)
    for row in data_list:
        table.append(row_format.format(*row))
    table.append(border)

    # Example table:
    # +----+---------------+--------------+
    # | id | name          | member_since |
    # +----+---------------+--------------+
    # | 1  | Souvic Das    | 20-07-2023   |
    # | 2  | Arkaprovo Das | 21-07-2023   |
    # | 3  | Sukrit Dutta  | 21-07-2023   |
    # | 4  | Shibam Dutta  | 21-07-2023   |
    # +----+---------------+--------------+
    return "\n".join(table)

# Data fetch functions
def get_from_table(table, _id = None):
    """Function to get details from table, optionally based on id. e.g. member details from members table"""

    if _id is None:
        cursor.execute(f"""SELECT * FROM {table}""")
    else:
        cursor.execute(
            f"""SELECT * FROM {table}
                WHERE id = %s""",
            (_id,)
        )
    return cursor.fetchall()

def input_member():
    """Function to get member data from user input"""
    _id = int(input("Please input the member's ID: "))
    member = get_from_table(MEMBERS, _id)
    if member:
        member = member[0]
    return _id, member

def get_issued_books(member_id):
    """Function to get books issued to a member"""

    cursor.execute(
        f"""SELECT * FROM {ISSUED_BOOKS}
            WHERE member_id = %s""",
        (member_id,)
    )
    return cursor.fetchall()


# The main loop of the program
MENU = f"""{MBORDER}
1. View Member Details
2. View Book Details
3. View Inventory
4. View Issued Books

5. Add a Member
6. Add a Book
7. Issue a Book

8. Show Menu Again
9. Exit
{MBORDER}"""

print(MENU)
while True:
    # This try-except block catches ValueError in case a string was input
    try:
        option = int(input("Please select an option (1-9): "))
    except ValueError:
        print(border("Please select an integer option from 1 to 9"))
        continue

    # If selected action is not within list of options
    if not 1 <= option <= 9:
        print(border("Selected option is out of range"))
        continue

    # If selected option is 1: View Member Details
    if option == 1:
        _id, m = input_member()
        if not m:
            print(border(f"Member with ID {_id} does not exist."))
            continue
        member = {
            "ID": m["id"],
            "Name": m["name"],
            "Member Since": date(m["member_since"])
        }
        print(border(pretty_dict(member)))

    # If selected option is 2: View Book Details
    elif option == 2:
        _id = int(input("Please input the book's ID: "))
        book = get_from_table(BOOKS, _id)
        if not book:
            print(border(f"Book with ID {_id} does not exist."))
            continue
        book = book[0]
        print(border(pretty_dict(format_book(book))))

    # If selected option is 3: View inventory
    elif option == 3:
        print(border(f'Books currently in inventory:\n{format_books(get_from_table(BOOKS), indent="    ")}'))

    # If selected option is 4: View Issued Books
    elif option == 4:
        _id, m = input_member()
        if not m:
            print(border(f"Member with ID {_id} does not exist."))
            continue

        issues = get_issued_books(_id)
        if issues is None or len(issues) == 0:
            print(
                border(f"Member {m['name']} (#{_id}) does not have any issued books.")
            )
            continue

        issues_list = []
        for issue in issues:
            issue_dict = {}

            book = get_from_table(BOOKS, issue["book_id"])[0]
            issue_dict["Book ID"] = book["id"]

            issue_dict["Issue Date"] = date(issue["issue_date"])

            issue_until = issue["issue_until"]
            issue_dict["Issue Until"] = date(issue_until)

            today = date()
            # If today is greater than expiry date aka expiry date has passed
            if today > issue_until:
                # Update fine amount based on fine per day
                issue_dict["Fine Amount"] = f"{(today - issue_until).days * FINE_PER_DAY}rs"

            issues_list.append(issue_dict)

        books = format_books(issues_list, indent="    ")
        print(
            border(f"Books issued to {m['name']} (#{_id}):\n{books}")
        )

    # If selected option is 5: Add a member
    elif option == 5:
        name = input("Please input name of the member: ").title()

        cursor.execute(
            (
                f"""INSERT INTO {MEMBERS} (name, member_since)
                VALUES (%s, CURDATE())"""
            ),
            (name,)
        )
        member_id = cursor.lastrowid
        con.commit()
        print(border(f"Added new member {name} (#{member_id})"))

    # If selected option is 6: Add a book
    elif option == 6:
        name = input("Please input name of the book: ")
        author = input("Please input author of the book: ").title()
        year = int(input("Please input publication year of the book: "))

        cursor.execute(
            (
                f"""INSERT INTO {BOOKS} (name, author, year)
                VALUES (%s, %s, %s)"""
            ),
            (name, author, year)
        )
        book_id = cursor.lastrowid
        con.commit()
        print(border(f"Added new book {name} (#{book_id})"))

    # If selected option is 7: Issue a book
    elif option == 7:
        member_id, m = input_member()
        if not m:
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
                "issued date": date(),
                "issued until": date()
                + datetime.timedelta(days=REINSTATEMENT_DAYS),
            }
        # If expiry date is less than today; issue has expired
        elif issued_book["issued until"] < date():
            renew = input("Renew issuance? y/N: ")
            if renew not in "yY":
                print("Aborted")
                continue
            issued_book["issued date"] = date()
            issued_book["issued until"] = date() + datetime.timedelta(
                days=REINSTATEMENT_DAYS
            )
        # Else, i.e. when expiry date is larger than today; issue hasn't expired yet
        else:
            remaining = (
                issued_book["issued until"] - date()
            ).days  # Difference (in days) between expiration date and today
            print(
                # This string is split into two halves to reduce the no. of characters in the line
                (
                    f"Book {book['name']} (#{book_id}) is already issued"
                    f" to {m['name']} (#{member_id}) for {remaining} more days"
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
                f" to {m['name']} (#{member_id}) for + {REINSTATEMENT_DAYS} days"
            )
        )

    # If selected option is 9: Show Menu Again, print the meny again
    elif option == 8:
        print(MENU)

    # If selected option is 9: Exit, break out of the loop
    elif option == 9:
        con.close()
        break
