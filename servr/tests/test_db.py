import sqlite3 as sql
import datetime as dt

class MockSQliteModel:
    def __init__(self, db):
        self.conn = sql.connect(db)
        self.cur = self.conn.cursor()

    def create_mock_table(self, table_name, fields):
        fields_to_str = ', '.join(f'{k} {v}' for k, v in fields.items())
        self.cur.execute(
            f'CREATE TABLE IF NOT EXISTS {table_name} ({fields_to_str})'
        )
        self.conn.commit()

    def read_table(self, table_name, conditions = None):
        query = f'SELECT * FROM {table_name}'

        if conditions:
            query += ' WHERE ' + \
                ' AND '.join(f'{k} = ?' for k in conditions.keys())
            self.cur.execute(query, list(conditions.values()))
        else:
            self.cur.execute(query)
        return self.cur.fetchall()
    
    def insert_row(self, table_name, data):
        placeholders = ', '.join('?' * len(data))
        fields = ', '.join(data.keys())

        try:
            self.cur.execute(
                f'INSERT INTO {table_name} ({fields}) VALUES ({placeholders})', list(data.values())
            )
            self.conn.commit()
        except sql.IntegrityError:
            print(f"Unable to write row. ID already exists in {table_name}")

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = MockSQliteModel('test')

    db.create_mock_table('test', {
        'id' : 'INTEGER PRIMARY KEY',
        'date' : 'DATE NOT NULL',
        'tips' : 'DECIMAL (2, 4)',
        'notes' : 'TEXT'
    })

    db.insert_row('test', {
        'id' : 1,
        'date': dt.date.today(),
        'tips' : 200.00,
        'notes' : ' '
    })

    print(db.read_table('test'))

    db.close()
