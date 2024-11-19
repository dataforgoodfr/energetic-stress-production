import sqlalchemy as sa
import pandas as pd

# change the URL_DB to the url of the postgres database
URL_DB = 'sqlite:///energy_forecast.db'

# tempo_classification table
tempo_classes = sa.Enum("BLUE", "WHITE", "RED", "Not Available", name="tempo_classification_enum")

metadata = sa.MetaData()
tempo_classification = sa.Table(
    'tempo_classification',
    metadata,
    sa.Column('date', sa.Date, nullable=False, primary_key=True),
    sa.Column('truth_by_RTE', tempo_classes, nullable=False),
    sa.Column('our_J_1', tempo_classes, nullable=False),
    sa.Column('our_J_2', tempo_classes, nullable=False),
    sa.Column('our_J_3', tempo_classes, nullable=False),
)

def init_db():
    engine = sa.create_engine(URL_DB)
    metadata.create_all(engine)
    
def get_all_tempo_classification():
    engine = sa.create_engine(URL_DB)
    with engine.connect() as connection:
        query = sa.select([tempo_classification])
        result = connection.execute(query)
        return result.fetchall()

def insert_tempo_classification(date, truth_by_RTE, our_J_1, our_J_2, our_J_3):
    engine = sa.create_engine(URL_DB)
    with engine.connect() as connection:
        query = tempo_classification.insert().values(
            date=date,
            truth_by_RTE=truth_by_RTE,
            our_J_1=our_J_1,
            our_J_2=our_J_2,
            our_J_3=our_J_3,
        )
        connection.execute(query)
        connection.commit()  # Ensure the transaction is committed

    
def add_the_csv_predictions(path_to_csv):
    mapping_cal_names = {
        "Type_de_jour_TEMPO": "truth_by_RTE",
        "our_tempo_J-1": "our_J_1",
        "our_tempo_J-2": "our_J_2",
        "our_tempo_J-3": "our_J_3",
        "index": "date",
    }
    df = pd.read_csv(path_to_csv, index_col=0)
    print(df.columns)
    
    df.index = pd.to_datetime(df.index).date
    for index, row in df.iterrows():
        row = row.fillna("Not Available")

        insert_tempo_classification(
            date=row.name,
            truth_by_RTE=row["Type_de_jour_TEMPO"],
            our_J_1=row["our_tempo_J-1"],
            our_J_2=row["our_tempo_J-2"],
            our_J_3=row["our_tempo_J-3"],
        )

def select_last_n_days(n_days):
    engine = sa.create_engine(URL_DB)
    with engine.connect() as connection:
        query = sa.select(tempo_classification).order_by(sa.desc(tempo_classification.c.date)).limit(n_days)
        print(query)
        result = connection.execute(query)
        results = result.fetchall()
        df = pd.DataFrame(results, columns=result.keys())
        df.set_index('date', inplace=True)  # Set the date as the index
        return df
    
if __name__ == '__main__':
    init_db()
    from energy_forecast import ROOT_DIR
    add_the_csv_predictions(ROOT_DIR / 'data' /"gold" / 'our_tempo_prediction.csv')
    
    selection = select_last_n_days(2)
    print(selection)

