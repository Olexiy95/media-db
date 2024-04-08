import csv
from sqlalchemy import MetaData, Table, Engine
from common.utils import create_connection_string, get_db_connection

# db_connection_string = create_connection_string(default_config=True)
# engine = get_db_connection(db_connection_string)


def check_csv_columns(csv_file, engine, table_name):
    try:
        metadata = MetaData(bind=engine)
        target_table = Table(table_name, metadata, autoload=True)

        target_columns = target_table.columns.keys()

        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file)

            header_row = next(csv_reader)

            if header_row == target_columns:
                print("Columns match!")
            else:
                print("Columns do not match!")

    except Exception as error:
        print("Error checking columns:", error)


def push_csv_data_to_psql(csv_file, engine: Engine, table_name):
    try:
        metadata = MetaData(bind=engine)
        target_table = Table(table_name, metadata, autoload=True)

        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file)

            next(csv_reader)

            insert_stmt = target_table.insert()

            for row in csv_reader:
                engine.execute(insert_stmt.values(row))

        print("Data inserted successfully!")
    except Exception as error:
        print("Error inserting data:", error)
