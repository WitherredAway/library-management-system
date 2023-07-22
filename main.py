import datetime

import mysql.connector as mcon


BORDER = "-" * 40
MBORDER = "=" * 40

FINE_PER_DAY = 10  # Fine amount per day in rupees
REINSTATEMENT_DAYS = 28  # No. of days to issue books for


# Make sure to create the 'library' database
con = mcon.connect(host="localhost", user="root", passwd="root")
# The dictionary kwarg ensures all output is a dictionary of col: value
cursor = con.cursor(dictionary=True)

# Names of the tables
MEMBERS = "members"
BOOKS = "books"
ISSUED_BOOKS = "issued_books"

# Initialize the database
cursor.execute("CREATE DATABASE IF NOT EXISTS library")
cursor.execute("USE library")

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
        [f"{indent}{key}: {value}" for key, value in dictionary.items()]
    )
    return details


def format_book(book):
    try:
        cursor.execute(
            f"""SELECT * FROM {ISSUED_BOOKS}
            WHERE book_id = %s""",
            (book["id"],),
        )
        issues = cursor.fetchall()
        return {
            "Book ID": book["id"],
            "Name": book["name"],
            "Author": book["author"],
            "Release Year": book["year"],
            "Issues": len(issues),
        }
    except KeyError:
        return book


def format_books(books, *, indent=""):
    """Function to nicely format a list of book dictionaries"""

    # This list comprehension is used to format each key and value of the book dictionary
    books_list = []
    for book in books:
        books_list.append(format_book(book))

    return "\n\n".join([pretty_dict(book, indent=indent) for book in books_list])


def tabulate(data):
    """Function to nicely tabulate data

    'data' has to be a list of dictionaries.
    The keys of these dictionaries will be the columns. E.g.:
    [
        {'id': 1, 'name': 'Souvic Das', 'member_since': datetime.date(2023, 7, 20)},
        {'id': 2, 'name': 'Arkaprovo Das', 'member_since': datetime.date(2023, 7, 21)},
        {'id': 3, 'name': 'Sukrit Dutta', 'member_since': datetime.date(2023, 7, 21)},
        {'id': 4, 'name': 'Shibam Dutta', 'member_since': datetime.date(2023, 7, 21)},
    ]
    """

    if len(data) == 0:
        return ""

    # Dictionary of each header and its largest value
    longest_row = max(data, key=lambda d: len(d))
    headers = {
        k: max([len(str(d.get(k, ""))) for d in data] + [len(k)])
        for k in longest_row.keys()
    }
    data_list = []

    # Loop through each row and put each value into a tuple
    for row in data:
        d = []
        for h in headers:
            v = row.get(h, "")
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
def get_from_table(table, _id=None, *, primary="id", n=None):
    """Function to get details from table, optionally based on id.
    e.g. member details from members table"""

    query = f"""SELECT * FROM {table}"""
    params = []
    if _id is not None and primary is not None:
        query += f"\nWHERE {primary} = %s"
        params.append(_id)

    if n is not None:
        query += "\nLIMIT %s"
        params.append(n)

    cursor.execute(query, params)
    return cursor.fetchall()


def print_table(table, *, n=None):
    """Function to print all members in the database"""

    table = get_from_table(table, n=n)
    print(tabulate(table))


def input_member():
    """Function to get member data from user input"""

    try:
        _id = int(input("Please input member ID: "))
    except ValueError:
        print(border("Member ID must be a number"))
        return None, None

    member = get_from_table(MEMBERS, _id)
    if member:
        member = member[0]
    else:
        print(border(f"Member with ID '{_id}' does not exist."))

    return _id, member


def input_book():
    """Function to get book data from user input"""

    try:
        _id = int(input("Please input book ID: "))
    except ValueError:
        print(border("Book ID must be a number"))
        return None, None

    book = get_from_table(BOOKS, _id)
    if book:
        book = book[0]
    else:
        print(border(f"Book with ID '{_id}' does not exist."))

    return _id, book


def get_issued_books(member_id):
    """Function to get books issued to a member"""

    issues = get_from_table(ISSUED_BOOKS, member_id, primary="member_id")
    return issues


# Functions for the main loop
def search(table, col):
    """Function to search a table's column and match them using LIKE"""

    search = input(f"Please input search string (will match {col}): ")
    if not search:
        print("Search string empty, showing all records")

    # Get all records where the specified cols match the search string
    cursor.execute(
        f"""SELECT * FROM {table}
        WHERE {col} LIKE %s
        ORDER BY LOCATE(%s, {col})""",
        (f"%{search}%", search),  # order by string location
    )
    data = cursor.fetchall()
    if not data:
        return print(border("No records found"))

    print(tabulate(data))


def edit(table, col):
    """Function to edit a row's column value"""

    cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
    primary = cursor.fetchone()["Column_name"]

    _id = input(f"""Editing '{table}'
    Please input '{primary}' of row to edit: """)
    entity = get_from_table(table, _id, primary=primary)
    if not entity:
        return print(border(f"Record with {primary} '{_id}' does not exist"))

    new = input(f"""Editing '{table}' #{_id}
    Please input new '{col}' value: """)
    if not new:
        return print(border("New value cannot be empty"))

    # Edit the values
    cursor.execute(
        (
            f"""UPDATE {table}
            SET {col} = %s
            WHERE {primary} = %s"""
        ),
        (new, _id),
    )
    con.commit()
    print(border(f"Edited '{table}' #{_id}'s '{col}' to '{new}'"))


def remove(table):
    """Function to remove a record from a table"""

    cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
    primary = cursor.fetchone()["Column_name"]

    _id = input(f"""Please input '{primary}' of row to delete from '{table}': """)
    entity = get_from_table(table, _id, primary=primary)
    if not entity:
        return print(border(f"Record with {primary} '{_id}' does not exist"))

    confirm = input(f"""{tabulate(entity)}
Are you sure you want to delete this record? y/N: """)
    if confirm not in "yY":
        print(border("Aborted"))
        return

    # Edit the values
    cursor.execute(
        (
            f"""DELETE FROM {table}
            WHERE {primary} = %s"""
        ),
        (_id,)
    )
    con.commit()
    print(border(f"Deleted record #{_id} from '{table}'"))


## Functions for the Members menu
def view_member():
    member_id, m = input_member()
    if not m:
        return

    issued_books = get_issued_books(member_id)

    member = {
        "Member ID": m["id"],
        "Name": m["name"],
        "Member Since": date(m["member_since"]),
        "Issued Books": len(issued_books),
        "Expired Issues": len([b for b in issued_books if b["issue_until"] < date()]),
    }
    print(border(pretty_dict(member)))


def add_member():
    name = input("Please input name of the member: ").title()
    if not name:
        print(border("Name cannot be empty"))
        return

    cursor.execute(
        (
            f"""INSERT INTO {MEMBERS} (name, member_since)
            VALUES (%s, CURDATE())"""
        ),
        (name,),
    )
    member_id = cursor.lastrowid
    con.commit()
    print(border(f"Added new member '{name}' (#{member_id})"))


## Functions for the Books menu
def view_book():
    book_id, book = input_book()
    if not book:
        return

    print(border(pretty_dict(format_book(book))))


def add_book():
    name = input("Please input name of the book: ")
    if not name:
        print(border("Name cannot be empty"))
        return
    author = input("Please input author of the book: ").title()
    if not author:
        print(border("Author cannot be empty"))
        return
    try:
        year = int(input("Please input publication year of the book: "))
    except ValueError:
        print(border("Year must be a number"))
        return

    cursor.execute(
        (
            f"""INSERT INTO {BOOKS} (name, author, year)
            VALUES (%s, %s, %s)"""
        ),
        (name, author, year),
    )
    book_id = cursor.lastrowid
    con.commit()
    print(border(f"Added new book '{name}' (#{book_id})"))


## Functions for the Issues menu
def view_issued_books():
    print_table(MEMBERS)
    _id, m = input_member()
    if not m:
        return

    issues = get_issued_books(_id)
    if not issues:
        print(border(f"Member '{m['name']}' (#{_id}) does not have any issued books."))
        return

    issues_list = []
    for issue in issues:
        issue_dict = {}

        book = get_from_table(BOOKS, issue["book_id"])[0]
        issue_dict["Issue ID"] = issue["issue_id"]
        issue_dict["Book ID"] = book["id"]
        issue_dict["Book Name"] = book["name"]

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
    print(f"Books issued to {m['name']} (#{_id}):", tabulate(issues_list), sep="\n")


def issue_book():
    print_table(MEMBERS)
    member_id, member = input_member()
    if not member:
        return

    print_table(BOOKS)
    book_id, book = input_book()
    if not book:
        return

    cursor.execute(
        f"""SELECT * FROM {ISSUED_BOOKS}
        WHERE member_id = %s
            AND book_id = %s""",
        (member_id, book_id),
    )
    issued_book = cursor.fetchone()

    if issued_book is None:
        cursor.execute(
            f"""INSERT INTO {ISSUED_BOOKS} (member_id, book_id, issue_date, issue_until)
            VALUES (%s, %s, %s, %s)""",
            (
                member_id,
                book_id,
                date(),
                date() + datetime.timedelta(days=REINSTATEMENT_DAYS),
            ),
        )
        con.commit()

    # If expiry date is less than today; issue has expired
    elif issued_book["issue_until"] < date():
        renew = input("Renew issuance? y/N: ")
        if renew not in "yY":
            print(border("Aborted"))
            return

        cursor.execute(
            f"""UPDATE {ISSUED_BOOKS}
            SET issue_date = %s,
                issue_until = %s
            WHERE member_id = %s
                AND book_id = %s""",
            (
                date(),
                date() + datetime.timedelta(days=REINSTATEMENT_DAYS),
                member_id,
                book_id,
            ),
        )
        con.commit()

    # Else, i.e. when expiry date is larger than today; issue hasn't expired yet
    else:
        remaining = (
            issued_book["issue_until"] - date()
        ).days  # Difference (in days) between expiration date and today
        print(
            # This string is split into two halves to reduce the no. of characters in the line
            (
                f"Book '{book['name']}' (#{book_id}) is already issued"
                f" to '{member['name']}' (#{member_id}) for {remaining} more day(s)"
            )
        )
        renew = input(f"Increase issuance period by {REINSTATEMENT_DAYS} days? y/N: ")
        if renew not in "yY":
            print(border("Aborted"))
            return

        cursor.execute(
            f"""UPDATE {ISSUED_BOOKS}
            SET issue_until = %s
            WHERE member_id = %s
                AND book_id = %s""",
            (date() + datetime.timedelta(days=REINSTATEMENT_DAYS), member_id, book_id),
        )
        con.commit()

    print(
        border(
            # This string is split into two halves to reduce the no. of characters in the line
            (
                f"Issued book '{book['name']}' (#{book_id})"
                f" to '{member['name']}' (#{member_id}) for + {REINSTATEMENT_DAYS} day(s)"
            )
        )
    )


# These are for the structure of the menus
MAINMENU_KEY = "0"
EXIT_KEY = "q"

MAINMENU = "main"
# The menu structure. It is a dictionary
# of menu: list pairs. These lists define
# all the options of that menu with tuples.
#
# The 1st element of which is the option text.
# The 2nd element either refers to another menu
# or a function to be executed, in which case
# the 3rd element optionally is a tuple of
# parameters for that function.
MENUS = {
    # Main menu
    MAINMENU: [
        ("Members", "members"),
        ("Books", "books"),
        ("Issues", "issues"),
    ],
    # Sub menus
    "members": [
        ("View All Members", print_table, (MEMBERS,)),
        ("Search Members", search, (MEMBERS, "name")),
        ("View Member Details", view_member),
        ("Add Member", add_member),
        ("Edit Member Details", "edit member"),
        ("Remove Member", remove, (MEMBERS,)),
    ],
    "books": [
        ("View Inventory", print_table, (BOOKS,)),
        ("Search Books", "search books"),
        ("View Book Details", view_book),
        ("Add Book", add_book),
        ("Edit Book Details", "edit book"),
        ("Remove Book", remove, (BOOKS,)),
    ],
    "issues": [
        ("View Issued Books", view_issued_books),
        ("Issue Book", issue_book),
        ("Un-Issue", remove, (ISSUED_BOOKS,)),
    ],
    # Sub menus of sub menus
    "search books": [
        ("Search Name", search, (BOOKS, "name")),
        ("Search Author", search, (BOOKS, "author")),
        ("Search Release Year", search, (BOOKS, "year"))
    ],
    "edit member": [
        ("Edit Name", edit, (MEMBERS, "name"))
    ],
    "edit book": [
        ("Edit Name", edit, (BOOKS, "name")),
        ("Edit Author", edit, (BOOKS, "author")),
        ("Edit Release Year", edit, (BOOKS, "year"))
    ]
}

_menu = MAINMENU  # This variable keeps track of which menu we're at
def menu():
    """Returns current menu options"""

    return MENUS[_menu]


def show_current_menu(indent="    "):
    """Shows current menu"""

    menu = MENUS[_menu]
    options = "\n".join(
        [f"{indent}{idx + 1}. {option[0]}" for idx, option in enumerate(menu)]
        + ["", f"{indent}{MAINMENU_KEY}. Main Menu", f"{indent}{EXIT_KEY}. Exit"]
    )
    text = f"""{_menu.title() + " Menu":^{len(MBORDER)}}
{BORDER}
{options}"""
    print(f"\033[33;1m{MBORDER}\n{text}\n{MBORDER}\033[0m")


def set_menu(menu):
    """Sets current menu"""

    global _menu
    _menu = menu

    show_current_menu()


# Main loop of the program
show_current_menu()
while True:
    current_menu = menu()
    option = input(
        f"""\033[34mPlease select '{_menu.title()}' menu option:
1-{len(current_menu)} or ENTER to show options
>>>\033[36m """
    )
    print("\033[32m")
    if option.lower() == EXIT_KEY:
        # Exit the program if exit key chosen
        con.close()
        break
    elif option == MAINMENU_KEY:
        # Skip if mainmenu option chosen or empty
        set_menu(MAINMENU)
        continue
    else:
        try:
            desc, *action = current_menu[int(option) - 1]
        except ValueError:
            # Show menu if non-integer input
            # Allows entering empty input to
            # see menu again
            show_current_menu()
            continue
        except IndexError:
            # Skip if chosen option is out of range
            print(border("Selected option is out of range."))
            continue

    if isinstance(action[0], str):
        # If action is string, select the menu corresponding to that string
        set_menu(action[0])
        continue
    else:
        # Else, call the corresponding function
        # using 3rd element as args
        # since it can only be str or function
        func = action[0]
        if len(action) > 1:
            params = action[1]
        else:
            params = ()
        func(*params)

