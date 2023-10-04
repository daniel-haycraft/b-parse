Documentation:
**requriment for new file.csv**
Transaction id, Full Name, Mailing addresss

**full name is just address you get from scrape**

**Hey**
Copy file path from csv file.
open terminal
run python __init__.py
enter/paste **shift+ctrl+V** your path hit enter on your key board



**Main.py** {
essential to running program. Run from here
this file reads the csv file and runs **alpha** and tbd __depreciated__ **bravo** that both require the list_dict
which is the CSV file converted into a dictionary
_AKA THIS IS WHERE ALL THE CODE IS FILTERED INTO_
}

Key definitions for variables ***definitions***:
li is from a for loop that iterates through a dictionary: Dictionary of imported keys and values from the csv file. 

__refrences__= LETTER and underscores are meant for referencing function inside other files and functions
eg.__E.__**detecting tags**


**akas**
**splitter = li['Full Name']**

-------------------------------------------------
**1** structer.py

**A.** **Update_to_csv**{
class object handles the updates to the li*:
}
------------------------------------------------------
**2**  **functs.py**

**B.** *splitting_chars_only* {
takes in sp which is also just **li['Full Name']**
*splitting_chars_only* is used for splitting the city, state, and zip code appending them to the back of the array from 
**li['Full Name']** 

the try and except statement is for when the length is less than the expected value which is 1 or more than 1

it also takes in to account that the length is supposed to be 5 but if its not it will remove the second index rather than the first index
}

**C.** **joining_ste_chars_four**{
specifically for suite numbers for addresses and connecting them with simple logic

takes in a lst which is just ***splitter**
when it applies the first index and second index are recorded then added together

the first index is then removed then the second index becomes the first index now. 

the new word created now replaces the first index
and the new list of is returned

}

**D.** **joining_ste_nums_three**{
just like the ^ above it sthe same logic but the indexes are all minus 1
}

**E.** **writer_row**{
**takes in the list_dict as majoras_mask**
takes in "majoras_mask" a stupid zelda reference
nevertheless this writes a csv file call r2_py2 and writes to a new csv file with the data from the whole **li**
}

**F.** **detecting_tags**{
Takes in a word == **splitter**
then specialized to the 0 index in which it checks to see if the company tags exist in the word_2[0]
if it does then word_2[0] is removed
}
------------------------------------------------------

**good_stuff.py**

**G.** **alpha**{
takes in the **list_dict** 
proceeds to update the fieldnames.
splitter variable comes in to play grabbing then splitting by line break
then using __F.__**detecting tags**
for the next part of this def i use length logic
Ignore anything == 1 or less
then I'll check for len if 3 then 
__B.__ **splitting_chars_only**
join the return from that function
then __A.__ **from structer import Append_to_csv as Charlie**
Charlie.handle_the_update does exactly what it says, It updates the

if len == 4 i use the __C.__**joining_ste_chars_four**
then __B.__ **splitting_chars_only**
then simple join
then update li
__A.__ **from structer import Append_to_csv as Charlie**

----------------
now in alpha i am chekcing to see if splitter starts with a number 

it will use the same logic just as before EXCEPT when the length == 3 
__D.__ **joining_ste_nums_three** will exist instead of nums_four 
}

*bravo* may be dismantaled
for changes