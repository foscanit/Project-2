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
        

def last_transforming():
    # Import new csv file (from the last function)
    horror_books = pd.read_csv("/Users/usuari/Desktop/Ironhack/BOOTCAMP/projects/project-II/Data/horror_books_2.csv",on_bad_lines='skip')
    
    def standard_birthplace(string):
        if string is not None:
            lista = string.split(",")
        if len(lista) == 3:
            return " ".join(lista[1:])
        elif len(lista) == 4:
            return " ".join(lista[1:3])
        elif len(lista) == 2:
            return string
        return string  
    
    horror_books['author_birthplace'] = horror_books['author_birthplace'].apply(standard_birthplace)
    
    def clean_birthplace(string):
        if 'New York' in string:
            return 'New York, U.S.'
        elif 'London' in string:
            return 'London, England'
        elif 'Dublin' in string:
            return 'Dublin, Ireland'
        else:
            return string
    
    horror_books['author_birthplace'] = horror_books['author_birthplace'].apply(clean_birthplace)
    
    horror_books = horror_books[horror_books['author_birthplace'] != 'Birthplace information not found']
    horror_books = horror_books[horror_books['author_birthplace'] != ']']
    horror_books = horror_books[horror_books['author_birthplace'] != 'Error: Unable to fetch Wikipedia page']
    
    return horror_books


# 1. What book genre is the most popular?

def first_graphic():
    
    lat_books = cleaning_before_webscraping()
    
    genre_count = lat_books.value_counts('genres')
    
    genre_count.plot(kind='bar', figsize=(13,7))
    plt.title('Novel genres that are more rated in Goodreads')
    plt.xlabel('Novel genres')
    plt.ylabel('Count')
    plt.xticks(rotation=45) 
    for index, value in enumerate(genre_count):
        plt.text(index, value + 4, str(value), ha='center')
    plt.show() 
    
    
def second_graphic():
    
    lat_books = cleaning_before_webscraping()
    
    # I'm going to drop the rows that have the values 'Erotica' and 'Science Fiction' in the column 'genre', because among the most rated books there aren't many of them belonging to these genres. 
    lat_books = lat_books[(lat_books['genres'] != 'Erotica') & (lat_books['genres'] != 'Science Fiction')]
    
    genre_ratings = lat_books.groupby('genres')['average_rating'].mean().reset_index()
    genre_ratings = genre_ratings.sort_values(by='average_rating', ascending=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=genre_ratings, x='genres', y='average_rating', palette='viridis')
    plt.xticks(rotation=90)  # Rotate the x-axis labels for better readability
    plt.xlabel('Genres')
    plt.ylabel('Average Rating')
    plt.title('Average Rating by Genre')
    plt.tight_layout()
    plt.show()

    # I calculate the average rating for each genre.
    # This plot will show me the average rating for each novel genre, allowing me to see how they relate to each other.
    

# 2. What novels are more popular, long or short ones? 

def t_graphic():
    lat_books = cleaning_before_webscraping()
    
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=lat_books, x='average_rating', y='num-pages', color='blue')
    plt.xlabel('Average Rating')
    plt.ylabel('Number of Pages')
    plt.title('Relationship Between Average Rating and Number of Pages')
    plt.tight_layout()
    plt.show()
    
def f_graphic():
    lat_books = cleaning_before_webscraping()
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=lat_books, x='genres', y='num-pages', palette='viridis')
    plt.xticks(rotation=90)
    plt.xlabel('Genres')
    plt.ylabel('Number of Pages')
    plt.title('Number of Pages by Genre')
    plt.tight_layout()
    plt.show()
    
# 3. Where are the most popular horror authors from?

def fifth_graphic():
    horror_books = last_transforming()
    
    # I'm going to drop the rows in which the value_counts of the column 'author_birthplace' equals 1. 

    value_counts = horror_books['author_birthplace'].value_counts()

    mask = horror_books['author_birthplace'].isin(value_counts[value_counts > 1].index)

    horror_books = horror_books[mask]
    horror_count = horror_books['author_birthplace'].value_counts()
    
    horror_count.plot(kind='bar', figsize=(16,7))
    plt.title("Horror Authors' birthplace")
    plt.xlabel('Regions and States')
    plt.ylabel('Count')
    plt.xticks(rotation=45) 
    for index, value in enumerate(horror_count):
        plt.text(index, value + 1, str(value), ha='center')
    plt.show()
    
# 4. Average age of the most popular horror authors.

def sixth_graphic():
    
    horror_books = last_transforming()
    
    # Convert 'author_birthdate' to integer with error handling
    try:
        horror_books['author_birthdate'] = horror_books['author_birthdate'].astype(int)
    except ValueError as e:
        # Handle the error, e.g., replace with NaN or a default value
        horror_books['author_birthdate'] = horror_books['author_birthdate'].apply(lambda x: int(x) if x.isdigit() else None)
    
    sns.set_context("poster")
    sns.set(rc={"figure.figsize": (12., 6.)})
    sns.set_style("whitegrid")

    sns.histplot(data=horror_books, x='author_birthdate', binwidth=5, color="#FFA07A")
    plt.title("Distribution of authors' birth years")
    plt.show()
    
# 5. Among popular horror authors, are there more men or women? 

def seventh_graphic():
    
    horror_books = last_transforming()
    
    gender_horror = horror_books['author_gender'].value_counts()
    gender_horror.plot.pie(autopct="%.1f%%");


