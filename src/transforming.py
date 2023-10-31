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