# rozetka_parser
Async rozetka parser
This scraper was created for educational reasons to learn async, not for commercial usage!

First run notebooksDB.py file to create table in your database
Second run links to file for backup.py file to collect fresh notebooks links and make backup
Than run Rozetka_parser.py and collect notebooks data to your postgresql database
If you want to collect images you can run Rozetka_notebooks_image_save, it reads pictures links from your database table an than save file to your computer
This was made only for notebooks data but you can easily change for any category, just change category_base_url in main() links to file for backup.py
PS be sure to have enough good proxies to make everything work fine
