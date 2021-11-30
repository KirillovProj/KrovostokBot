from config import conn
import quotes


def create_tables() -> None:
    """
    Creates three tables in connected database.
    Songs contains song_id (serializes), name of the song and YouTube link.
    Quotes contains quote_id (serializes), text of the quote and reference to song_id.
    Users contains user_id *NOT SERIAL* and last received quote id that references Quotes.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
            DROP TABLE IF EXISTS Users, Quotes, Songs CASCADE
            ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Songs(
            song_id SERIAL PRIMARY KEY, name VARCHAR(50), link VARCHAR(60)
            );
            CREATE TABLE IF NOT EXISTS Quotes(
            quote_id SERIAL PRIMARY KEY, text VARCHAR(200), song_id INTEGER REFERENCES Songs(song_id)
            );
            CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY, last_quote INTEGER REFERENCES Quotes(quote_id)
            );
            ''')


def fill_content_tables() -> None:
    """
    Fills tables Songs and Quotes with data from quotes.py.
    Check quotes.py to get an understanding on how to arrange your data properly.
    """
    with conn:
        cur = conn.cursor()
        for i in quotes.songs:
            cur.execute('''
                INSERT INTO Songs(name, link) VALUES(%s, %s);
                ''', (i[0], i[1]))
        for key, value in quotes.quotes.items():
            cur.execute('''
                INSERT INTO Quotes(text, song_id) VALUES(%s, %s);
                ''', (key, value))


def add_user(user_id: int) -> None:
    """
    Adds user_id to table Users. Last_quote becomes None until updated later.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO Users(user_id) VALUES(%s);
        ''', (user_id,))


def get_user_ids() -> set[int]:
    """
    Returns set of user_ids that are currently in the table Users.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT user_id FROM Users;
        ''')
        return set([user[0] for user in cur.fetchall()])


def get_number_of_quotes() -> int:
    """
    Counts number of quotes in table Quotes.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT count(*) FROM Quotes;
        ''')
        return cur.fetchone()[0]


def get_quote_by_id(id: int) -> str:
    """
    Takes quote id as an argument and returns text of the quote in row.
    If id is incorrect, will send TypeError which is being handled with plug-string.
    """
    with conn:
        cur = conn.cursor()
        try:
            cur.execute('''
            SELECT text FROM Quotes WHERE quote_id=%s;
            ''', (id,))
        except TypeError:
            return 'Шило сегодня с похмелья и не может выйти на сцену'
        return cur.fetchone()[0]


def get_last_quote(user_id: int) -> int:
    """
    Takes user_id and returns last_quote recorded in the row with same user_id.
    Will send TypeError if there is no quote (quote_id is None). It is handled in main module.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT last_quote FROM Users WHERE user_id=%s;
        ''', (user_id,))
        return cur.fetchone()[0]


def update_last_quote(quote_id: int, user_id: int) -> None:
    """
    Updates table Users changing last_quote for a given user_id to new quote_id.
    """
    with conn:
        cur = conn.cursor()
        cur.execute('''
        UPDATE Users SET last_quote = %s WHERE user_id = %s;
        ''', (quote_id, user_id))


def get_song_name(user_id: int) -> str:
    """
    Takes user_id, with it searches for last_quote in table Users.
    Using last_quote id returns name of the song from which this quote originated.
    """
    quote_id = get_last_quote(user_id)
    with conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT s.name FROM Songs s 
        INNER JOIN Quotes q ON s.song_id = q.song_id
        WHERE q.quote_id = %s;
        ''', (quote_id,))
        return cur.fetchone()[0]


def get_song_link(user_id: int) -> str:
    """
    Takes user_id, with it searches for last_quote in table Users.
    Using last_quote id returns YouTube link for the song from which this quote originated.
    """
    quote_id = get_last_quote(user_id)
    with conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT s.link FROM Songs s 
        INNER JOIN Quotes q ON s.song_id = q.song_id
        WHERE q.quote_id = %s;
        ''', (quote_id,))
        return cur.fetchone()[0]
