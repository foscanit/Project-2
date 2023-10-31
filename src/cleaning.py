# Importing libraries.

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns
import numpy as np
import os
import re
import requests
from bs4 import BeautifulSoup
import time
import spacy
import gender_guesser.detector as gender_detector

def cleaning_before_webscraping():
    
    # I explain here the steps previous to the web scraping process.
    
    # Import csv file.
    books = pd.read_csv("/Users/usuari/Desktop/Ironhack/BOOTCAMP/projects/project-II/Data/books_genres.csv",on_bad_lines='skip')
    
    # Rename columns
    books = books.rename(columns={'  num_pages': 'num_pages'})
    books.columns = [i.lower().replace(" ", "_") for i in books.columns]
    
    # Dropping two useless columns
    books.drop(['isbn13', 'isbn'], axis=1, inplace=True)
    
    # Creating a new column
    pattern = r'(\d{4})'
    books['years'] = books['publication_date'].str.extract(pattern)
    
    def author_name(string):
        standardized_name = re.sub(r'\s+', '_', string)
        # Add a period (.) before each uppercase letter (except the first one and spaces)
        standardized_name = re.sub(r'(?<=[a-zA-Z])(?=[A-Z])', '._', standardized_name)
        # Add a period (.) before each uppercase letter following a period
        standardized_name = re.sub(r'\.(?=[A-Z])', '._', standardized_name)
        
        if standardized_name == 'Newt_Scamander/J._K._Rowling':
            return 'J._K._Rowling'
        else:
            return standardized_name
    
    # Applying the function written above
    books['author'] = books['author'].apply(author_name)
    
    # Creating a new dataframe
    book_author = books[['title', 'author']]
    
    # From this new dataframe I'm going to create another one, in which the rows with multiple authors only keep the first author.

    new_rows = []

    for index, row in book_author.iterrows():
        authors = row['author'].split('/')
        if len(authors) > 1:
        # If there are multiple authors, I keep only the first author
            first_author = authors[0]
            new_row = {'title': row['title'], 'author': first_author}
            new_rows.append(new_row)
        else:
        # If there is only one author, keep the original row
            new_rows.append({'title': row['title'], 'author': row['author']})

    # The new DataFrame with the updated rows
    new_books = pd.DataFrame(new_rows)

    # Reset the index
    new_books.reset_index(drop=True, inplace=True)
    
    #I add the columns from the original dataframe that interest me.

    new_books['average_rating'] = books['average_rating']
    new_books['language_code'] = books['language_code']
    new_books['num-pages'] = books['num_pages']
    new_books['ratings_count'] = books['ratings_count']
    new_books['text_reviews_count'] = books['text_reviews_count']
    new_books['publisher'] = books['publisher']
    new_books['genres'] = books['genres']
    new_books['years'] = books['years']
    
    # I create three empty columns in this new dataframe (which I will fill afterwards with web scraping data from wikipedia): 
    # 'author_birthplace', 'author_birthdate', 'author_gender'.

    new_books['author_birthplace'] = None
    new_books['author_birthdate'] = None
    new_books['author_gender'] = None
    
    # I'm going to drop the names of the authors that are not in a latin alphabet.

    latin_pattern = re.compile(r'^[a-zA-Z_. ]+$')  
    lat_books = new_books[new_books['author'].str.match(latin_pattern)]
    
    # I'm going to drop the rows in which the column of 'ratings_count' are less than 1000, because I want to analyze the most rated books.

    lat_books = lat_books[lat_books['ratings_count'] >= 1000]

    # I want to focuse on novels, so I'm going to drop the short stories:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Short Stories')].index)

    # I also want to focuse on Fiction:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Nonfiction')].index)

    # I want to exclude comics and manga:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Comics')].index)
    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Manga')].index)

    #I'm goint to exclude Poetry as well:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Poetry')].index)

    # and I'll exclude plays:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Plays')].index)

    #I'm also Childrens' Animal and Picture Books:

    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Animals')].index)
    lat_books = lat_books.drop(lat_books[lat_books['genres'].str.contains('Picture Books')].index)

    # I don't want any set but individual books:
    lat_books = lat_books.drop(lat_books[lat_books['title'].str.contains('Set')].index)
    lat_books = lat_books.drop(lat_books[lat_books['title'].str.contains('Collection')].index)
    
    def clean_genres(string):
        if 'Horror' in string:
            return 'Horror'
        elif 'Science Fiction' and 'Fantasy' in string:
            return 'Fantasy & Science Fiction'
        elif 'Fiction' and 'Historical' in string:
            return 'Historical novel'
        elif 'Fiction' and 'Thriller' in string:
            return 'Thriller'
        elif '20th Century' in string:
            return '20th Century Fiction'
        elif 'Classics' in string:
            return 'Classics'
        elif 'Science Fiction' in string:
            return 'Science Fiction'
        elif 'Contemporary' in string:
            return 'Contemporary Fiction'
        elif 'Erotica' in string:
            return 'Erotica'
        elif 'European' and 'Fiction':
            return 'European Literature'
        else:
            return string
    
    # I apply the function above to clean book genres:
    lat_books['genres'] = lat_books['genres'].apply(clean_genres)
   
    return lat_books

def transforming_webscraping():
    
    lat_books = cleaning_before_webscraping()
    
    # Since it's almost Halloween, I'm going to create a new dataframe with only Horror novels.
    horror_books = lat_books[lat_books['genres'] == 'Horror']
    
    # I'm going to keep only the horror novels that are better rated, above 3.9
    horror_books = horror_books[horror_books['average_rating'] >= 3.9]
    
    def birthyear_f(string):
        name = string
        base_url = 'https://en.wikipedia.org/wiki'
        endpoint = '/' + name
        url = base_url + endpoint
    
        try:
            res = requests.get(url)
            res.raise_for_status()  # Check for request success
            time.sleep(4)
            soup = BeautifulSoup(res.content, 'html.parser')
        
            # Attempt to find the birthplace information
            birth_raw = soup.find("td", {"class": "infobox-data"})
        
            if birth_raw is not None:
                birth_info = birth_raw.getText().replace("(", "\n").replace(")", "\n")
                birth_info = re.sub(r'(\d+)', r'\1\n', birth_info)
                birth_list = birth_info.split('\n')
                birth_year = birth_list[1]
                return birth_year
            else:
                return "Birthyear information not found"
    
        except requests.exceptions.RequestException as e:
            return "Error: Unable to fetch Wikipedia page"
        except Exception as e:
            return "An error occurred: " + str(e)
    
    # Webscraping from Wikipedia with the above function to fill the 'author_birthdate' column.
    horror_books['author_birthdate'] = horror_books['author'].apply(birthyear_f)
    
    def birthplace_f(string):
        name = string
        base_url = 'https://en.wikipedia.org/wiki'
        endpoint = '/' + name
        url = base_url + endpoint
    
        try:
            res = requests.get(url)
            res.raise_for_status()  # Check for request success
            time.sleep(2)
            soup = BeautifulSoup(res.content, 'html.parser')
        
            # Attempt to find the birthplace information
            birth_raw = soup.find("td", {"class": "infobox-data"})
        
            if birth_raw is not None:
                birth_info = birth_raw.getText().replace("(", "\n").replace(")", "\n")
                birth_info = re.sub(r'(\d+)', r'\1\n', birth_info)
                birth_list = birth_info.split('\n')
                birth_list[-1]
                author_birthplace = birth_list[-1]
                return author_birthplace
            else:
                return "Birthplace information not found"
    
        except requests.exceptions.RequestException as e:
            return "Error: Unable to fetch Wikipedia page"
        except Exception as e:
            return "An error occurred: " + str(e)
    
    # Webscraping from Wikipedia with another function above to fill the 'author_birthplace' column.
    horror_books['author_birthplace'] = horror_books['author'].apply(birthplace_f)
    
    def guess_gender_new(string):
        # Instantiate the detector
        d = gender_detector.Detector()
        names = string.split('_')
    
        # Define a dictionary of specific names and genders
        specific_names = {
            'Wilkie_Collins': 'male',
            'Raynold_Gideon': 'male',
            'Laurell_K._Hamilton': 'female',
            'C._S._Friedman': 'female',
            'L._A._Banks': 'female',
            'Tananarive_Due': 'female',
            'V._C._Andrews': 'female',
            'Sandy_Petersen': 'male',
            'Mary_Higgins_Clark': 'female',
            'Charlie_Huston': 'male',
            'Natsuo_Kirino': 'female'
        }
    
        # Check if the name is in the specific names dictionary
        if string in specific_names:
            return specific_names[string]
        else:
            first_name = names[0]
            # Guess the gender
            gender = d.get_gender(first_name)
            return gender
    
    # With another function, I fill values from the 'author_gender' column.
    horror_books['author_gender'] = horror_books['author'].apply(guess_gender_new)
    
    # I save my dataframe with the information from web scraping saved, just in case.

    horror_books.to_csv("horror_books_2.csv", index=False)

    # Specify the folder path and filename for the CSV file
    folder_path = "/Users/usuari/Desktop/Ironhack/BOOTCAMP/projects/project-II/Data"
    file_name = "horror_books_2.csv"

    # Combine the folder path and filename to create the full file path
    full_file_path = f"{folder_path}/{file_name}"

    # Export the DataFrame to the specified folder
    horror_books.to_csv(full_file_path, index=False)