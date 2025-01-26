import os
import base64
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd

def sqlQuery(query: str) -> pd.DataFrame:
    """
    Executes a query against the Databricks SQL Warehouse and returns the result as a Pandas DataFrame.
    """
    cfg = Config()
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID')}",
        credentials_provider=lambda: cfg.authenticate,
        staging_allowed_local_path="/tmp"  # Required for file ingestion commands
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()

def list_catalogs() -> pd.DataFrame:
    """
    Returns the list of catalogs in the Databricks SQL Warehouse.
    """
    query = "SHOW CATALOGS"
    return sqlQuery(query)

def list_schemas(catalog: str) -> pd.DataFrame:
    """
    Returns the list of schemas in a specific catalog.
    """
    query = f"SHOW SCHEMAS IN {catalog}"
    return sqlQuery(query)

def list_tables(catalog: str, schema: str) -> pd.DataFrame:
    """
    Returns the list of tables in a specific catalog and schema.
    """
    query = f"SHOW TABLES IN {catalog}.{schema}"
    return sqlQuery(query)

def describe_table(catalog: str, schema: str, table: str) -> pd.DataFrame:
    """
    Returns the schema of a specified table.
    """
    query = f"DESCRIBE TABLE {catalog}.{schema}.{table}"
    return sqlQuery(query)

def get_sample_data(catalog: str, schema: str, table: str, limit: int = 10) -> pd.DataFrame:
    """
    Retrieves sample data from a specified table.

    Args:
        catalog (str): The catalog name.
        schema (str): The schema name.
        table (str): The table name.
        limit (int): Number of sample rows to fetch (default: 10).

    Returns:
        pd.DataFrame: DataFrame containing sample rows from the table.
    """
    query = f"SELECT * FROM {catalog}.{schema}.{table} LIMIT {limit}"
    return sqlQuery(query)

def save_file_to_volume(encoded_content: str, volume_path: str, file_name: str, overwrite: bool = True) -> str:
    """
    Saves an uploaded file to a Databricks volume using the PUT command.

    Args:
        encoded_content (str): Base64 encoded file content.
        volume_path (str): The target Databricks volume path (e.g., "dbfs:/Volumes/my_catalog/uploads/").
        file_name (str): The name of the file to be saved.
        overwrite (bool): Whether to overwrite the existing file.

    Returns:
        str: The full path of the saved file.
    """
    try:
        # Decode base64 content and save to a temporary local file
        content_string = encoded_content.split(",")[1]
        decoded = base64.b64decode(content_string)
        local_temp_path = f"/tmp/{file_name}"

        with open(local_temp_path, "wb") as f:
            f.write(decoded)

        # Construct the Databricks volume file path
        databricks_file_path = f"{volume_path}/{file_name}"
        overwrite_option = "OVERWRITE" if overwrite else ""

        # Execute the Databricks SQL command to upload file
        query = f"PUT '{local_temp_path}' INTO '{databricks_file_path}' {overwrite_option}"
        sqlQuery(query)

        print(f"File successfully uploaded to: {databricks_file_path}")
        os.remove(local_temp_path)  # Cleanup local temp file
        return databricks_file_path

    except Exception as e:
        print(f"Error uploading file to volume: {str(e)}")
        return None
    
def read_file_from_volume(volume_path: str, file_name: str, delimiter: str = ",", escape_char: str = '"', header: int = 0, encoding: str = "utf-8", limit: int = 10) -> pd.DataFrame:
    """
    Reads a CSV file from a Databricks volume using read_files function.
    """
    try:
        file_path = f"{volume_path}/{file_name}"
        
        # Using read_files function with CSV options
        query = f"""
        SELECT * FROM read_files(
            '{file_path}',
            format => 'csv',
            header => {str(header == 0).lower()},  -- true if header=0, false otherwise
            delimiter => '{delimiter}',
            escape => '{escape_char}',
            charset => '{encoding}'
        )
        LIMIT {limit}
        """
        
        df = sqlQuery(query)
        
        # If no header (header is None), rename columns to Column_1, Column_2, etc.
        if header is None:
            # First, check if the first row was read as header (it shouldn't be)
            if df.shape[0] > 0:  # If we have data
                # Rename existing columns to Column_1, Column_2, etc.
                df.columns = [f"Column_{i+1}" for i in range(len(df.columns))]
                
                # If the first row contains what was supposed to be header data,
                # we need to prepend it back to the dataframe
                first_row = df.iloc[0]
                df = pd.concat([pd.DataFrame([first_row.values], columns=df.columns), df], ignore_index=True)
        
        return df

    except Exception as e:
        print(f"Error reading file from volume: {str(e)}")
        return pd.DataFrame()