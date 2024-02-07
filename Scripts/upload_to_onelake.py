import os
import argparse
import sqlite3
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient,
)
from azure.identity import DefaultAzureCredential
import pandas as pd

def get_db_connection() -> sqlite3.Connection:
    """creates a connection to the databse"""
    conn = sqlite3.connect(r'..\MinFlaskApp\database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_books():
    """Get all the book in the books database table and return as a dataframe"""
    conn = get_db_connection()
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return books_df

def get_service_client_token_credential(account_name: str) -> DataLakeServiceClient:
    """Create a service client using the default Azure credential"""
    account_url = f"https://{account_name}.dfs.fabric.microsoft.com"
    token_credential = DefaultAzureCredential()
    return DataLakeServiceClient(account_url, credential=token_credential)

def create_file_system_client(service_client, file_system_name: str) -> FileSystemClient:
    file_system_client = service_client.get_file_system_client(file_system = file_system_name)
    return file_system_client

def create_directory_client(file_system_client : FileSystemClient, path: str) -> DataLakeDirectoryClient:
    directory_client = file_system_client.get_directory_client(path)
    return directory_client

def list_directory_contents(file_system_client: FileSystemClient, directory_name: str):
    paths = file_system_client.get_paths(path=directory_name)

    for path in paths:
        print(path.name + '\n')

def upload_string_to_directory(directory_client: DataLakeDirectoryClient, target_name: str, data: str):
    file_client = directory_client.get_file_client(target_name)
    file_client.upload_data(data, overwrite=True)

def upload_file_to_directory(directory_client: DataLakeDirectoryClient, local_path: str):
    file_name=os.path.basename(local_path)

    with open(file=local_path, mode="rb") as data:
        upload_string_to_directory(directory_client, file_name, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload books to Onelake")
    parser.add_argument("-a", "--account_name", default="onelake", help="Account name")
    parser.add_argument(
        "-w", "--workspace_name",
        default="81ebd6c4-e449-4d0d-a53d-bf9913c74630",
        help="GUID for workspace",
    )
    parser.add_argument(
        "-d", "--data_path",
        default="b81f64bb-fe0e-4495-a598-4b0b0fe48926/Files/books",
        help="GUID from ABFS path + folder",
    )
    parser.add_argument(
        "-n", "--name",
        default="upload.csv",
        help="name for uploaded file",
    )
    args = parser.parse_args()

    account_name = args.account_name
    workspace_name = args.workspace_name
    data_path = args.data_path
    name = args.name

    books_df = get_all_books()
    print(books_df.head())
    books_csv = books_df.to_csv(index=False)

    service_client = get_service_client_token_credential(account_name)
    file_system_client = create_file_system_client(service_client, workspace_name)
    directory_client = create_directory_client(file_system_client, data_path)
    upload_string_to_directory(directory_client, name, books_csv)
    print("File uploaded!!\n")
    list_directory_contents(file_system_client, data_path)

    # for path in paths:
    #     print(path.name + "\n")
    #     print ("Hello Admin")
    # else:
    #     print ("Hello Guest")