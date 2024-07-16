import sqlite3 as sql

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

    print(db.read_table('test'))

    db.close()
