import sqlalchemy as sa

metadata = sa.MetaData()

connection = {
    'user': 'Your user name',  # input your postgres username
    'database': 'your database name',  # input your database name here
    'host': '127.0.0.1',  # change your host if it's not local
    'password': 'your password'  # input your password for this database
}

dsn = 'postgresql://{user}:{password}@{host}/{database}'.format(**connection)

Ad = sa.Table(
    'rozetka_justPrice', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('date', sa.Date, nullable=True),
    sa.Column('name', sa.String),
    sa.Column('status', sa.String),
    sa.Column('price', sa.Integer),
    sa.Column('procesor', sa.String),
    sa.Column('diagonal', sa.String),
    sa.Column('memory', sa.String),
    sa.Column('OS', sa.String),
    sa.Column('procesor gen', sa.String),
    sa.Column('color', sa.String),
    sa.Column('optic drive', sa.String),
    sa.Column('HDD', sa.String),
    sa.Column('picture', sa.String),
    sa.Column('description', sa.String),
)

if __name__ == '__main__':
    engine = sa.create_engine(dsn)
    metadata.drop_all(engine)
    metadata.create_all(engine)
