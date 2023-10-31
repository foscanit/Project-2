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

import src.cleaning as clean
import src.transforming as trans 
import src.visualizing as vis

if __name__ == '__main__':
    clean.cleaning_before_webscraping()
    clean.transforming_webscraping()
    trans.last_transforming()
    vis.first_graphic()
    vis.second_graphic()
    vis.t_graphic()
    vis.f_graphic()
    vis.fifth_graphic()
    vis.sixth_graphic()
    vis.seventh_graphic()
    
    
