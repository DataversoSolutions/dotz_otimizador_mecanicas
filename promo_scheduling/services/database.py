from typing import Protocol
from google.cloud import bigquery


class PDatabaseAdapter(Protocol):
    def productivity_base(self, partner_name, mechanic_name):
        ...


class BigqueryDatabaseAdapter:
    query = "SELECT * FROM `{project}.{dataset_id}.{table_id}`"

    def __init__(self, project, dataset_id, table_id):
        self.project = project
        self.dataset_id = dataset_id
        self.table_id = table_id
        self._data_table_df = None
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = bigquery.Client()
        return self._client

    @property
    def data_table_df(self):
        if self._data_table_df is None:
            query_response = self.client.query(
                self.query.format(
                    project=self.project,
                    dataset_id=self.dataset_id,
                    table_id=self.table_id,
                )
            )
            self._data_table_df = query_response.to_dataframe()

        return self._data_table_df

    def productivity_base(self, partner_name, mechanic_name):
        df_filter = self.data_table_df.loc[
            (self.data_table_df["NomeParceiro"] == partner_name)
            & (self.data_table_df["PromoAjust"].isin([mechanic_name]))
        ]
        if df_filter["Days"].sum() == 0:
            result = 0
        else:
            result = df_filter["Clientes"].sum() / df_filter["Days"].sum()
        return result
