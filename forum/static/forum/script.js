// CSRF token for PUT requests
var csrftoken = getCookie('csrftoken');


// Event listener for all button clicks
document.addEventListener('click', event => {
    
    /* 
    IMPORTANT: Posts and comments are mostly treated the same
    in this script. Event handling and updates to the DOM are 
    the same, but API requests differ. Thus, POSTS AND COMMENTS
    ARE REFERRED TO USING THE UMBRELLA TERM "item." Importantly, 
    comments inherit a lot of the post HTML attributes (class 
    names) for styling convenience; the div containers for 
    comments and posts have different class names, however 
    */

    // Store the clicked button and the item's (post's or
    // comment's) HTML element
    const element = event.target;
    var item = element.parentNode;

    // User clicks Edit button
    if (element.className === 'btn btn-outline-warning') {
        edit_item(item);
    }

    // User clicks Save Edits button
    if (element.className === 'btn btn-outline-primary') {
        save_edits(item);
    }

    // User submits new comment
    if (element.className === 'btn btn-info') {
        create_comment();
    }

    // User clicks Like button 
    if (element.id === 'like-button') {
        like_item(item);
    } 
    
    // User clicks Like icon (inside of Like button)
    if (element.id === 'like-icon') {
        item = item.parentNode;
        like_item(item);
    }
});


// Updates the DOM when the user clicks the Edit button
function edit_item(item) {

    // Store the item (post or comment) content and declare 
    // a variable to store the image link
    const item_content = item.querySelector('.post-content');
    var item_image_link;

    // If the item has an image, retrieve the image link
    try {
        item_image_link = item.querySelector('.post-img').src;
    }
    // Otherwise, set the image link equal to an empty string
    catch {
        item_image_link = '';
    }
    const timestamp = item.querySelector('.post-timestamp');

    // Create a new HTML textarea that is pre-populated with
    // the item content and a pre-populated image link field
    const edit_text_area = document.createElement('textarea');
    edit_text_area.className = 'edit-post-textarea';
    edit_text_area.innerHTML = item_content.textContent;
    const image_link_field = document.createElement('textarea');
    image_link_field.className = 'edit-post-image-link';
    image_link_field.innerHTML = item_image_link;

    // Replace the item content with the pre-populated textarea 
    item.replaceChild(edit_text_area, item_content);
    item.insertBefore(image_link_field, timestamp);

    // Create a Save button for saving edits
    const save_button = document.createElement('button');
    save_button.className = 'btn btn-outline-primary';
    save_button.innerHTML = 'Save Edits';
    item.insertBefore(save_button, timestamp);

    // Remove the Edit button
    item.removeChild(item.querySelector('.btn-outline-warning'));
}


// Saves the edits a user makes to their own items (posts or
// comments) in the database and updates the DOM
function save_edits(item) {
    
    // Store the updated item content and updated image link
    const new_content = item.querySelector('.edit-post-textarea').value;
    const img_link = item.querySelector('.edit-post-image-link').value;

    // Check if the item is a post or a comment before making
    // an API request
    var api_route;

    // Item is a post
    if (item.className === 'post-div') {
        api_route = `/forum/${parseInt(item.dataset["post"])}`;
    }
    
    // Item is a comment
    else if (item.className === 'comment-div') {
        api_route = `/forum/comment/${item.dataset["comment"]}`;
    }

    // Send a PUT request to the item ID's route
    fetch(api_route, {
        headers: {
            'X-CSRFToken': csrftoken
        },
        method: 'PUT',
        body: JSON.stringify({
            content: new_content,
            image_link: img_link
        })
    })
    .then(() => {

        // Update the DOM. First, replace the textarea with
        // a paragraph element
        const item_content_paragraph = document.createElement('p');
        item_content_paragraph.className = 'post-content';
        item_content_paragraph.innerHTML = new_content;
        item.replaceChild(item_content_paragraph, item.querySelector('.edit-post-textarea'));
        
        // Remove the image link field and Save button
        item.removeChild(item.querySelector('.edit-post-image-link'));
        item.removeChild(item.querySelector('.btn-outline-primary'));

        // Check if there is an image and create an Edit button
        // to be added later
        var item_image = item.querySelector('.post-img');
        const edit_button = document.createElement('button');
        edit_button.className = 'btn btn-outline-warning';
        edit_button.innerHTML = 'Edit';
        
        // The item already contains an image
        if (item_image) {

            // If the user supplies an image link,
            // update the image element's src field and 
            // add an Edit button immediately before 
            // the image element
            if (img_link) {
                item_image.src = img_link;
                item.insertBefore(edit_button, item_image);
            } 

            // If the user supplies no image link, 
            // delete the image element and add an Edit 
            // button immediately before the content element 
            else {
                item.removeChild(item_image);
                item.insertBefore(edit_button, item_content_paragraph);
            }
        } 

        // The item does not contain an image
        else {
            
            // If the user supplies an image link,
            // create a new image element and add
            // an Edit button immediately before it
            if (img_link) {
                const new_item_image = document.createElement('img');
                new_item_image.className = 'post-img';
                new_item_image.src = img_link;
                item.insertBefore(new_item_image, item_content_paragraph);
                item.insertBefore(edit_button, new_item_image);
            } 

            // If the user supplies no image link, 
            // add an Edit button immediately before
            // the content element
            else {
                item.insertBefore(edit_button, item_content_paragraph);
            }
        }
    })

    // Error handling
    .catch(error => {
        console.log('Error:', error);
    });
}


// Updates a user's likes and the item's (post's or comment's)
// like count in the database and updates the DOM   
function like_item(item) {
    
    // Check if the item is a post or a comment before making
    // an API request. Store the item ID and viewer's username for 
    // requests. Also create a boolean that indicates whether the 
    // viewer has liked the item and store the user API route
    var item_id;
    const viewer_name = document.querySelector('.posts-page').dataset["viewer"];
    var already_liked = false;
    const user_api_route = `/forum/${viewer_name}`;

    // Item is a post
    if (item.className === 'post-div') {
        item_id = parseInt(item.dataset["post"]);

        // Make a GET request to the username's route to see
        // if the user has liked the post
        fetch(user_api_route)

        // Convert response to JSON data
        .then(response => response.json())

        // Update the boolean variable if the user has
        // already liked the post
        .then(user => {
            user.likes.forEach(function(liked_post) {
                if (liked_post.id === item_id) {
                    already_liked = true;
                }
            }); 
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });

        // Send a PUT request to the post ID's route
        fetch(`/forum/${item_id}`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: 'PUT',
            body: JSON.stringify({
                like: true 
            })
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });

        // Send a PUT request to the viewer's route
        fetch(`/forum/${viewer_name}`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: 'PUT',
            body: JSON.stringify({
                post_id: item_id
            })
        })
        .then(() => {
            update_like_count(item, already_liked);
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });
    }
    
    // Item is a comment
    else if (item.className === 'comment-div') {
        item_id = parseInt(item.dataset["comment"]);

        // Make a GET request to the username's route to see
        // if the user has liked the comment
        fetch(user_api_route)

        // Convert response to JSON data
        .then(response => response.json())

        // Update the boolean variable if the user has
        // already liked the comment
        .then(user => {
            user.comment_likes.forEach(function(liked_comment) {
                if (liked_comment.id === item_id) {
                    already_liked = true;
                }
            }); 
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });

        // Send a PUT request to the comment ID's route
        fetch(`/forum/comment/${item_id}`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: 'PUT',
            body: JSON.stringify({
                like: true 
            })
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });

        // Send a PUT request to the viewer's route
        fetch(`/forum/${viewer_name}`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: 'PUT',
            body: JSON.stringify({
                comment_id: item_id
            })
        })
        .then(() => {
            update_like_count(item, already_liked);
        })

        // Error handling
        .catch(error => {
            console.log('Error:', error);
        });
    }
}


// Updates an item's like count in the DOM
function update_like_count(item, already_liked) {
    var like_count_element = item.querySelector('.post-likecount');
    var like_count = parseInt(like_count_element.innerHTML);
    if (already_liked) {
        like_count -= 1;
        like_count_element.innerHTML = like_count;
    }
    else {
        like_count += 1;
        like_count_element.innerHTML = like_count;
    }
}

// Creates a new comment on a post by making an API call
// to the comments route
function create_comment() {

    // Remove any existing error messages
    if (document.querySelector('.comment-error-message')) {
        document.querySelector('.comment-error-message').remove();
    }
    
    // Check the content length and image link length. First,
    // store the content and image link and initialize some
    // variables that appear a few times
    const content = document.querySelector('#post-textarea').value; 
    const image_link = document.querySelector('#post-image-link').value;
    var error_message = document.createElement('strong');
    error_message.className = 'comment-error-message';
    const form = document.querySelector('form');
    const viewer_name = document.querySelector('.posts-page').dataset["viewer"];

    // Check that the comment content is not an empty string
    // and that the length of the content does not exceed 1000
    // characters
    if (!content || content.length > 1000) {
        
        // Display an error message in the DOM
        error_message.innerHTML = 'Error! Your post content must not be empty and cannot exceed 1000 characters.'
        form.appendChild(error_message);
        return 
    }

    // Check that the image URL length does not exceed 3000 
    // characters
    if (image_link.length > 3000) {
        
        // Display an error message in the DOM
        error_message.innerHTML = 'Error! Your image URL cannot exceed 3000 characters.'
        form.appendChild(error_message);
        return 
    }

    // Store the post ID
    const post_id = document.querySelector('.post-div').dataset["post"];

    // Send a POST request to the /emails route
    fetch(`/forum/comment/compose/${post_id}`, {
        headers: {
            'X-CSRFToken': csrftoken
        },
        method: 'POST',
        body: JSON.stringify({
            content: content,
            image_link: image_link
        })
    })

    // Convert response to JSON data 
    .then(response => response.json())
    .then(comment => {

        // Update the DOM. First clear the form text fields
        document.querySelector('#post-textarea').value = '';
        document.querySelector('#post-image-link').value = '';

        // Increase the comment number displayed in the Comments button
        var comment_button = document.querySelector('#comment-button');
        var comment_number = parseInt(comment_button.innerText.slice(10));
        comment_number += 1;
        comment_button.innerHTML = `Comments (${comment_number})`;

        // Add a new comment element to the DOM
        var parent_element = document.querySelector('.all-comments-div');
        var new_comment = document.createElement('div');
        new_comment.className = 'comment-div';
        new_comment.setAttribute('data-comment', comment.id);
        new_comment.innerHTML = `<h5><a href="${comment.author}" class="post-user">${comment.author}</a></h5>`;
        new_comment.innerHTML += `<button type="button" class="btn btn-outline-warning">Edit</button>`;
        if (comment.image_link) {
            new_comment.innerHTML += `<img class="post-img" src=${comment.image_link}>`;
        }
        new_comment.innerHTML += `<p class="post-content">${comment.content}</p>`;
        new_comment.innerHTML += `<p class="post-timestamp">${comment.timestamp}</p>`;
        new_comment.innerHTML += `<button class="btn" id="like-button"><i class='far fa-thumbs-up' id="like-icon"></i></button>`;

        // Setting the margin of the like count does not work without specifying it 
        // in JavaScript (CSS not being read). Added a style attribute here to 
        // fix this issue
        new_comment.innerHTML += `<p class="post-likecount" style="margin-left: 6.5px">${comment.num_likes}</p>`;
        new_comment.innerHTML += `<hr>`;
        parent_element.prepend(new_comment);
    })

    // Error handling
    .catch(error => {
        console.log('Error:', error);
    });
}


// Provides a CSRF token for PUT requests. 
// Source: https://docs.djangoproject.com/en/3.0/ref/csrf/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();

            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
