# Foorum

## Overview

Foorum is a simple web forum that enables users to submit posts on discussion boards with distinct topics. Signed in users are able to create and edit posts on each board and can like and comment on other users' posts. Users also have the ability to follow other users and can view those users' posts in a separate page. If given permission by an administrator, users may create new discussion boards. The app utilizes Django on the back-end to enable users to create new posts and boards, sort posts, and follow and unfollow other users. On the front-end, JavaScript lets users create new comments and edit and like posts and comments via the app's API. 

## Models

Foorum includes the following models:
- User
- Post
- Board
- Comment

The **User** model stores information about each user, including the users they follow, their followers, and the posts and comments they have liked. 

The **Post** model stores information about each post on a discussion board. This includes the post's author, the post's associated discussion board, the post's content, an optional image, the post's like count, and the post's timestamp.

The **Board** model stores a discussion board's name and description.

The **Comment** model stores information about a comment on a post. In particular, it stores a comment's author, associated post, content, like count, and timestamp. This model also stores an optional image. 

## Templates

Foorum is a multipage application and comprises eight HTML files, listed below.
- layout.html (layout inherited by each template)
- login.html (login page)
- register.html (new user registration page) 
- index.html
- board.html
- user.html
- following.html
- comments.html

**index.html** is the page all users land on when opening Foorum. It lists all of the existing discussion boards as links. Users who have been granted permission by an administrator also see a form for creating new discussion boards below the list of boards.

**board.html** is the page all users see after clicking on a link to a discussion board. The page displays the name and description of the board and a sortable list of posts associated with the board. Signed in users also see a form to create new posts. 

**user.html** is the page all users see after clicking on a user's name in a post or comment. The page displays the user's follower count, following count (number of users they follow), and all of the user's posts in reverse chronological order. Signed in users also have the ability to follow and unfollow the user. 

**following.html** is the page a signed in user sees after clicking on the "Following" link at the top of the screen. The page displays all posts authored by users followed by the signed in user. Users who are not signed in cannot see the link to this page.

**comments.html** is the page all users see after clicking on the Comments button under a post. The page displays the original post and all of the comments associated with the post in reverse chronological order. Signed in users also see a form to create new comments. 
 
## Static Files

The **static** directory contains a JavaScript file and a CSS file.

- script.js
- styles.css

**script.js** creates a dynamic user interface for the app. In particular, it lets users create new comments, edit posts and comments, and like posts and comments using the app's API. The app uses JavaScript from Bootstrap and Popper to create a dropdown sort button on each board.  

**styles.css** styles the app's templates and helps make the app mobile-responsive. The app uses Bootstrap and Font Awesome for additional styling (e.g. buttons and the like icon).

## Additional Information

I was able to incorporate most of the desired features in this project, with the exception of a notification system (best outcome). I was also hoping to embed YouTube videos in posts and comments, but more essential features took precedence. I also encountered a minor issue when editing posts and comments. If a user edits a post or comment that includes a link in the content, the link will display as normal text (not clickable) when the user saves their edits using the API. Since URLs in the post content are converted to clickable links using Django's urlize filter, the user must reload the page in order for the URL text to become a link. This isn't a huge issue, but it is still annoying. I hope to continue working on Foorum and resolve these issues soon.