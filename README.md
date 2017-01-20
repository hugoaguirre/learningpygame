# learningpygame
Having fun with pygame

![alt tag](https://c1.staticflickr.com/1/373/32294204791_0dc815d79c_c.jpg)

## Install dependencies

You need to have pip installed, refer to https://pip.pypa.io/en/stable/installing/ for installation instructions.

Then you can run the following command to install dependencies

    make install

## Run

Simply run

    make

or

    python main.py

## Contribute

Go to https://github.com/juanjosegzl/learningpygame/issues?q=is%3Aopen+is%3Aissue+label%3Aeasy
those tickets are marked to be easy to start contributing.

If you need help comment the ticket with your questions or, if you have one, your approach to solve the ticket.

### Git flow

If you are not used to git you can read this chapter https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository or follow this recipe.

    git checkout master
    git pull origin master
    git checkout -b <name_of_your_branch>  # creates a branch where you can code
    git add <the file you need to commit>
    git commit  # will open an editor, write a comment there
    git push --set-upstream origin <name_of_your_branch>

Once your changes are pushed, you can go to https://github.com/juanjosegzl/learningpygame and create a new Pull Request
Search for the buttom Compare & pull request