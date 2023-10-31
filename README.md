# project-II-pipelines

# Overview

The aim of this project was to clean, analyze and expand the information through web scraping of a Goodread's dataset from 2019, updated in 2022 (and found in Kaggle). This dataset contains information about many books in various categories, and I have used this data to produce visualizations in order to either prove or disprove my hypotheses.
<br>

# Requirements/Libraries Used:
This code was written in Python/Jupyter Notebook, using the following libraries:
<br>
- Numpy
- Pandas
- matplotlib.pyplot
- Seaborn
- bs4
- Requests
- BeautifulSoup
- Time
- Gender-guesser
<br>
 

# Hypotheses:
<br>

## 1- Fantasy & Science Fiction novels are the most popular books.
## 2- Long novels (with at least 500 pages) are more popular than short ones.
## 3- The most popular horror authors are from regions where Halloween is strongly celebrated.
## 4-  The most popular horror authors are really old or dead. 
## 5- Among the popular horror authors, there are more men than women. 

<br>

# Workflow/ Methodology:

## 1. Data exploring and preprocessing

First of all, I imported the Goodreads' dataset downloaded from Kaggle and I started to explore it. It was a huge dataframe with 11123 rows and 12 columns. For the data preprocessing, I modified the column's names, and I checked how many null values and duplicated were there. Then I erased two columns that weren't useful for my research. With a regex pattern I created the values of a new column, 'years', that would extract each year from the values of 'publication_date'. I did that because in the begining I had an hypothesis related to the years, but then I changed my mind, and I decided to focus on other hypothesis. 

## 2. Data transforming

The first problem I had to face was the fact that for each book sometimes there were multiple authors. I wanted to analyze individual authors, and besides I realized that most of the names after the principal author referred to illustrators or translators instead of secondary authors (not always but often). 

Before solving the issue of multiple authors, I created and applied a function to standardize the names in the "author" column, so that afterwards I could use them for web scraping through Wikipedia. 

Then, I iterated through the author names and made a list of dictionaries in order to keep only the first authors (in the case of the multiple authors' rows) but keeping the original rows, in the case of the individual authors. With this list of dictionaries I created a new dataframe made up of the 'author' and 'title' columns. Then I added the other columns from the previous dataframe that interested me, and I also created three empty columns with the intention of filling them through Web scraping. 

After that, with the purpose of filtering more the dataset and focus on what I was really interested (the most popular novels) I dropped the book genres that weren't useful (short stories, nonfiction, comics and manga, poetry, plays, children's books and collections or sets). I also filtered the dataset dropping the names of the authors that weren't written in the latin alphabet (such as arabic or chinese, as I cannot understand them), and I dropped the rows in which the column of 'ratings_count' were less than 1000, because I wanted to analyze the most rated books (to check later the average ratings).


Another problem I had to face was the genre column, because each row had a lot of different tags (regarding the book category) so I created and applied a function to clean the genre. At this point of the analysis, I was able to answer the first two hypothesis.


## 3. Web scraping

Since it was almost Halloween, I decided that for the following questions I would focus on Horror novels, so I created a new dataframe with only this genre. I wanted to analyze the most popular authors, so I kept the novels that were better rated, over 3.9. Then I created two functions based on web scraping through Wikipedia that could extract the authors' birthyears and birthplaces. My computer works really slow and sometimes gets stuck while web scraping, but luckily the functions worked and were able to extract the information of 84.9% authors (aprox).  

I tried to fill the column of 'author_gender' via Web scraping but I didn't success, so at last I created a function with the library Gender-guesser. Depending on the first name this function would try to detect the gender of the author and return either male, female, mostly male, mostly female, androgynous or unknown. The interesting thing about this function is that after applying it for the first time, I had 25 unknown genders, and most of them belonged to women. The function had not detected them because they wouldn't use their first name in the book cover, but instead their initials, probably trying to sell more books by not making evident that they were women. After cleaning the results, I was able to respond the last hypothesis. 

## 4. Last transformations

I created another function to standardize the authors' birthplaces, in order to keep only the name of the city/region/state plus the country. After that last cleaning, I was finally able to answer hypothesis 3 and 4. 



# Fantasy & Science Fiction novels are the most popular books:

In this first inquiry, I received conclusive results, Fantasy and Science Fiction is the most popular genre among novels (there are novels in this dataset that are labelled with both categories). In second and third place, we have Historical novels and Thrillers. Fantasy and Science Fiction novels are not only the most rated books among fiction titles but also the ones that have higher average ratings in Goodreads.

![image1](https://github.com/foscanit/Project-2/blob/main/images/novel_genres.png)
![image2](https://github.com/foscanit/Project-2/blob/main/images/genres_ratings.png) 



#  Long novels (with at least 500 pages) are more popular than short ones.

I didn't quite get it right in this case. According to the plot, the most rated books have between 200 and 500 pages, but the best average ratings (4.5) don't really have a pattern, there can be both really short novels or books with around 1200 pages.

If we take a look to the second image, where we relate the genres with the average number of pages, we can check that the longest fiction books are Horror and Historical novels, although they are not the most popular genres. 

<br>

![image3](https://github.com/foscanit/Project-2/blob/main/images/ratings_pages.png)
![image4](https://github.com/foscanit/Project-2/blob/main/images/pages_genres.png)



# The most popular horror authors are from regions where Halloween is strongly celebrated.


So according to the results of my research this hypotesis completely makes sense. The country where most of the horror authors are from (the most popular) is United States. And the first five states are Pennsylvania, Maine, New York, Arkansas and Massachusets. We should take into consideration some facts. 4 of these 5 states belong to the north east coast of U.S., the regions were pilgrims first arrived (i.e. the english and irish colons that brang the celtic tradition of Samhain, the origin of Halloween). 

And according to this website (https://www.goodhousekeeping.com/holidays/halloween-ideas/g4607/history-of-halloween/): 

"The holiday we celebrate as Halloween today really started taking off in the U.S. in the middle of the 19th century, when a wave of Irish immigrants left their country during the potato famine. The newcomers brought their own superstitions and customs, including the jack-o'-lantern. But back then, they carved them out of turnips, potatoes and beets instead of pumpkins". 

And let's not forget the witches's trials in Salem (Massachusets) and its connection with the state of Main. The history of these states definitely influenced the horror authors' imagination: https://www.mainememory.net/sitebuilder/site/772/page/1181/display

In addition, I have found out that Pennsylvania is the state where more horror movies have been filmed, probably due to its mysterious landscapes: https://delawarevalleyjournal.com/horror-movie-mecca-pennsylvania-is-the-deadliest-state/

![image5](https://github.com/foscanit/Project-2/blob/main/images/regions_countries.png) 


# The most popular horror authors are really old or dead. 

The plot shows us that the average birthyear of the most popular authors is 1945... so yeah, maybe not dead yet but old. 

![image6](https://github.com/foscanit/Project-2/blob/main/images/ages.png)


# Among the popular horror authors, there are more men than women. 

This is (purtroppo) a definitely true hypothesis, among the most popular authors, 105 are male and only 34 female. 

![image7](https://github.com/foscanit/Project-2/blob/main/images/male_female.png)



# In Conclusion

- Fantasy and Science Fiction is the most rated genre in Goodreads and apparently also the most popular type of novel.
- Long novels aren't the most popular ones. On the other hand, the most rated novels are between 200 and 500 pages, being 200 pages not considered a long novel (at least if you ask regular readers). 
- US is the country where Halloween is most celebrated, specially in some specific states, so it makes sense that the most popular horror authors are American.
- The most popular authors of horror books are quite old. Is it because young generations don't know how to scare? Do they lack imagination? Are social networks depriving us from boredom and therefore from genuine and macabre creativity?  
- The horror literature is still a genre dominated by men, and we've seen as well that the few popular women often use their initials instead of their first name, in order to not be seen as "female writers".
