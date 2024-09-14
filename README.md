## Social Media Application Setup

Setup consists of multiple steps, which are as follows
1. Clone the repository
2. Spin container
    ```sh
    $ docker compose build
    $ docker compose up -d
    ```
3. Run following commands 
    ```sh
    $ docker exec -it socialmedia_container python manage.py loaddata users.json
    $ docker exec -it socialmedia_container python manage.py createsuperuser
    ```

4. Postman Collection is provided in the repository itself
    with filename __Assignment_postman_collection.json__

Note : default password for all the dummy users is __test@1234__