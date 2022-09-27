from typing import Protocol
import pandas as pd
from google.cloud import bigquery


class PDatabaseAdapter(Protocol):
    def productivity_base(self, partner_name, mechanic_name):
        ...


class BigqueryDatabaseAdapter:
    project = "dotzcloud-datalabs-datascience"
    dataset_id = "DATA_SCIENCE_TEMP"
    table_id = "OTIMIZADOR_DADOS"

    def __init__(self, project, dataset_id, table_id):
        self.project = project
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._data_table_df: pd.DataFrame = None
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = bigquery.Client()
        return self._client

    @property
    def data_table_df(self):
        if not self._data_table_df:
            dataset_ref = bigquery.DatasetReference(self.project, self.dataset_id)
            table_ref = dataset_ref.table(self.table_id)
            table = self.client.get_table(table_ref)
            self._data_table_df = self.client.list_rows(table).to_dataframe()
        return self._data_table_df

    def productivity_base(self, partner_name, mechanic_name):
        df_filter = self.data_table_df.loc[(df['NomeParceiro'] == partner_name) & (
            self.data_table_df['PromoAjust'].isin(mechanic_name))]
        if df_filter['DistinctDays'].sum() == 0:
            result = 0
        else:
            result = df_filter['Clientes'].sum() / df_filter['DistinctDays'].sum()
        return result
