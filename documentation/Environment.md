# .env Variables Explained

- There should be an .env file with the following variable with correct parameters (do not have the values in quotes)

| Variable                          | Description                                                           |
|-----------------------------------|-----------------------------------------------------------------------|
| OPENAI_API_KEY                    | Your secret key for accessing the OpenAI API.        |
| DEFAULT_MODEL                     | The default OpenAI model to use for parsing and embedding (e.g. “gpt-4.1-mini”). |
| DEFAULT_CV_STORAGE_PATH           | Filesystem path where uploaded CVs are saved locally (e.g. `./cv_storage`). |
| DEFAULT_VECTORDB_STORAGE_PATH     | Directory path for persisting the Chroma vector database (e.g. `./vectordb`). |
| MARIADB_USERNAME                  | Username for connecting to your MariaDB instance.                    |
| MARIADB_PASSWORD                  | Password for authenticating the MariaDB user.                        |
| MARIADB_HOST                      | Hostname or IP address of the MariaDB server (e.g. `localhost`).     |
| MARIADB_PORT                      | TCP port on which MariaDB is listening (default is `3306`).           |
| MARIADB_DATABASE                  | Name of the MariaDB database/schema used to store CV