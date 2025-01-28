import os
import base64
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd
import time

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
        # Check file size (limit to 100MB for example)
        content_string = encoded_content.split(",")[1]
        file_size = len(base64.b64decode(content_string))
        max_size = 100 * 1024 * 1024  # 100MB

        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum limit of {max_size/1024/1024}MB")

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
        raise
    
def read_file_from_volume(volume_path: str, file_name: str, delimiter: str = ",", quote_char: str = '"', header: bool = True, encoding: str = "utf-8", limit: int = 10) -> pd.DataFrame:
    """
    Reads a CSV file from a Databricks volume using read_files function.
    """
    try:
        file_path = f"{volume_path}/{file_name}"
        
        query = f"""
        SELECT * FROM read_files(
            '{file_path}',
            format => 'csv',
            header => {str(header).lower()},
            delimiter => '{delimiter}',
            quote => '{quote_char}',
            charset => '{encoding}'
        )
        LIMIT {limit}
        """
        
        df = sqlQuery(query)
        
        if df.empty:
            return df
            
        # Generate column names only if no header
        if not header:
            df.columns = [f"col_{i}" for i in range(len(df.columns))]
        
        # Ensure all column names are strings
        df.columns = [str(col).strip() for col in df.columns]
        
        return df

    except Exception as e:
        print(f"Error reading file from volume: {str(e)}")
        return pd.DataFrame()

def insert_data_to_table(catalog: str, schema: str, table: str, data: pd.DataFrame, file_path: str, header: bool = True, delimiter: str = ",", quote_char: str = '"', encoding: str = "utf-8") -> None:
    """Insert data into a Databricks table."""
    try:
        # Get just the filename from the path
        filename = file_path.split("/")[-1]
        
        # Construct the insert query using read_files
        columns = ", ".join(data.columns)
        insert_query = f"""
            INSERT INTO {catalog}.{schema}.{table} ({columns})
            SELECT {columns} FROM read_files(
                '{file_path}',
                format => 'csv',
                header => {str(header).lower()},
                delimiter => '{delimiter}',
                quote => '{quote_char}',
                charset => '{encoding}'
            )
        """
        
        # Execute using existing sqlQuery function
        sqlQuery(insert_query)
            
    except Exception as e:
        print(f"Error in insert_data_to_table: {str(e)}")
        raise Exception(f"Failed to insert data: {str(e)}")