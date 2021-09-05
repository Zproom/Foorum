// CSRF token for PUT requests
var csrftoken = getCookie('csrftoken');


// Event listener for all button clicks
document.addEventListener('click', event => {
    
    /* 
    IMPORTANT: Posts and comments are treated the same in 
    this script. Event handling and updates to the DOM are 
    the same. Posts and comments are both referred to with the
    umbrella term "item." Importantly, comments inherit a lot of 
    the post HTML attributes (class names) for styling convenience; 
    the div containers for comments and posts have different class
    names, however 
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

    // Store the item (post or comment) content
    const item_content = item.querySelector('.post-content');
    const timestamp = item.querySelector('.post-timestamp');

    // Create a new HTML textarea that is pre-populated with
    // the item content and an image upload button
    const edit_text_area = document.createElement('textarea');
    edit_text_area.className = 'edit-post-textarea';
    edit_text_area.innerHTML = item_content.textContent;
    const img_label = document.createElement('label');
    img_label.for = 'img';
    img_label.innerHTML = 'Attach an Image (Optional):';
    const image_link_field = document.createElement('input');
    image_link_field.type = 'file';
    image_link_field.name = 'img';
    image_link_field.id = 'image-upload-button';
    image_link_field.style = 'margin-left:7px';

    // Store the item ID (comment or post ID)
    var item_id;
    if (item.className === 'post-div') {
        item_id = parseInt(item.dataset["post"]);
    }
    else if (item.className === 'comment-div') {
        item_id = parseInt(item.dataset["comment"]);
    }

    // Make a GET request to the item's route to retrieve
    // the item's embedded media link. A GET request is required
    // here (instead of extracting the link from the iframe) because
    // the link in the iframe is changed after the original post is made,
    // creating problems when editing SoundCloud songs
    var item_video_link;
    const item_api_route = `/forum/${item_id}`;
    fetch(item_api_route)

    // Convert response to JSON data
    .then(response => response.json())

    // Store the embedded link
    .then(data => {
        item_video_link = data.video;
        const video_link_field = document.createElement('textarea');
        video_link_field.id = 'post-textarea-small';
        video_link_field.placeholder = 'Add a link to a YouTube video or SoundCloud song (optional). \
                                        You will need to refresh the page to view the updated media.';
        video_link_field.innerHTML = item_video_link;

        // Replace the item content with the pre-populated textarea and add
        // other fields
        item.replaceChild(edit_text_area, item_content);
        item.insertBefore(img_label, timestamp);
        item.insertBefore(image_link_field, timestamp);
        item.insertBefore(video_link_field, timestamp);

        // Create a Save button for saving edits
        const save_button = document.createElement('button');
        save_button.className = 'btn btn-outline-primary';
        save_button.id = 'submit-post-comment';
        save_button.innerHTML = 'Save Edits';
        item.insertBefore(save_button, timestamp);

        // Remove the Edit button
        item.removeChild(item.querySelector('.btn-outline-warning'));
    })

    // Error handling
    .catch(error => {
        console.log('Error:', error);
    });
}


// Saves the edits a user makes to their own items (posts or
// comments) in the database and updates the DOM
function save_edits(item) {
    
    // Remove any existing error messages
    if (item.querySelector('.comment-error-message')) {
        item.querySelector('.comment-error-message').remove();
    }
    
    // Initialize variables
    const item_video_upload = item.querySelector('#post-textarea-small').value;
    const new_content = item.querySelector('.edit-post-textarea').value;
    const timestamp = item.querySelector('.post-timestamp');
    var error_message = document.createElement('strong');
    error_message.className = 'comment-error-message';

    // Check that the comment content is not an empty string
    // and that the length of the content does not exceed 1000
    // characters
    if (!new_content || new_content.length > 1000) {
        
        // Display an error message in the DOM
        error_message.innerHTML = 'Error! Your post content must not be empty and cannot exceed 1000 characters.'
        item.insertBefore(error_message, timestamp);
        return 
    }

    // Store the item ID (comment or post ID)
    var item_id;
    if (item.className === 'post-div') {
        item_id = parseInt(item.dataset["post"]);
    }
    else if (item.className === 'comment-div') {
        item_id = parseInt(item.dataset["comment"]);
    }

    // Declare a variable (form_data) to store the 
    // content the user has entered in the form. The form
    // should store the text in the text area and the image
    // and video files if they exist
    var form_data = new FormData();
    form_data.append('content', new_content);
    form_data.append('img_file', item.querySelector('#image-upload-button').files[0]);
    form_data.append('video_link', item_video_upload);
    
    // Create a boolean variable that indicates whether the user uploaded a new image  
    var uploaded_new_img;
    if (item.querySelector('#image-upload-button').value) {
        uploaded_new_img = true;
    }
    else {
        uploaded_new_img = false;
    }

    // Use Ajax to make a PUT request that includes the content, image file, and video link
    $.ajax({ 
        url: `/forum/${item_id}`,  
        type: 'PUT',
        headers: {
            "X-CSRFToken": csrftoken
        },
        data: form_data,
        processData: false,
        contentType: false,
        success: function(data) { 

            // Update the DOM. First, replace the textarea with
            // a paragraph element. NOTE: The video won't reflect
            // any updates until the page is refreshed
            const item_content_paragraph = document.createElement('p');
            item_content_paragraph.className = 'post-content';
            item_content_paragraph.innerHTML = data.content;
            item.replaceChild(item_content_paragraph, item.querySelector('.edit-post-textarea'));
        
            // Remove the image upload button, video label, video field, and Save button
            item.removeChild(item.querySelector('#image-upload-button'));
            item.removeChild(item.querySelector('label'));
            item.removeChild(item.querySelector('#post-textarea-small'));
            item.removeChild(item.querySelector('.btn-outline-primary'));

            // Check if the post already has an image and video and create an Edit button
            // to be added later
            var item_image = item.querySelector('.post-img');
            const item_video = item.querySelector('.video-embedded');
            const edit_button = document.createElement('button');
            edit_button.className = 'btn btn-outline-warning';
            edit_button.innerHTML = 'Edit';
        
            // The item already contains an image
            if (item_image) {

                // If the user uploaded an image,
                // update the image element's src field
                if (uploaded_new_img) {
                    item_image.src = data.thumb;

                    // Add an Edit button immediately before the image
                    item.insertBefore(edit_button, item_image);
                } 

                // If the user did not upload a new image, 
                // delete the image element
                else {
                    item.removeChild(item_image);

                    // If the item already contains a video, add an Edit button
                    // immediately before the video. Otherwise, add the 
                    // button immediately before the text. Recall: The user
                    // must refresh the page to view updates to YouTube/SoundCloud media
                    if (item_video) {
                        item.insertBefore(edit_button, item_video);
                    }
                    else {
                        item.insertBefore(edit_button, item_content_paragraph);
                    }
                }
            } 

            // The item does not contain an image
            else {
            
                // If the user uploaded an image,
                // create a new image element
                if (uploaded_new_img) {
                    const new_item_image = document.createElement('img');
                    new_item_image.className = 'post-img';
                    new_item_image.src = data.thumb;

                    // If the item already contains a video, add the image immediately 
                    // before the video. Then, add an Edit button
                    // immediately before the image. Otherwise, add the 
                    // image immediately before the text and the Edit button before
                    // the image. Recall: The user must refresh the page to view updates 
                    // to YouTube/SoundCloud media
                    if (item_video) {
                        item.insertBefore(new_item_image, item_video);
                        item.insertBefore(edit_button, new_item_image);
                    }
                    else {
                        item.insertBefore(new_item_image, item_content_paragraph);
                        item.insertBefore(edit_button, new_item_image);
                    }
                } 

                // The user did not upload a new image
                else {

                    // If the item already contains a video, add the Edit button immediately 
                    // before the video. Otherwise, add the Edit button immediately
                    // before the text. 
                    if (item_video) {
                        item.insertBefore(edit_button, item_video);
                    }
                    else {
                        item.insertBefore(edit_button, item_content_paragraph);
                    }
                }
            }
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}


// Creates a new comment on a post by making an API call
// to the comments route
function create_comment() {

    // Remove any existing error messages
    if (document.querySelector('.comment-error-message')) {
        document.querySelector('.comment-error-message').remove();
    }
    
    // Initialize variables
    const item_video_upload = document.querySelector('#post-textarea-small').value;
    const content = document.querySelector('#post-textarea').value;     
    var error_message = document.createElement('strong');
    error_message.className = 'comment-error-message';
    const form = document.querySelector('form');

    // Check that the comment content is not an empty string
    // and that the length of the content does not exceed 1000
    // characters
    if (!content || content.length > 1000) {
        
        // Display an error message in the DOM
        error_message.innerHTML = 'Error! Your post content must not be empty and cannot exceed 1000 characters.'
        form.appendChild(error_message);
        return 
    }

    // Store the post ID
    const post_id = document.querySelector('.post-div').dataset["post"];

    // Store the form data in a FormData object
    var form_data = new FormData();
    form_data.append('content', content);
    form_data.append('img_file', document.querySelector('#image-upload-button').files[0]);
    form_data.append('video_link', item_video_upload);
    form_data.append('csrfmiddlewaretoken', csrftoken)

    // Use Ajax to make a POST request that includes the content and image file
    $.ajax({ 
        url: `/forum/comment/compose/${post_id}`,  
        type: 'POST',
        data: form_data,
        processData: false,
        contentType: false,
        success: function(data) { 

            // Update the DOM. First clear the form text fields. 
            // Recall: The user must refresh the page to view updates 
            // to YouTube/SoundCloud media, so the comment created below
            // does not contain any embedded content
            document.querySelector('#post-textarea').value = '';
            document.querySelector('#image-upload-button').value = '';

            // Increase the comment number displayed in the Comments button
            var comment_button = document.querySelector('#comment-button');
            var comment_number = parseInt(comment_button.innerText.slice(10));
            comment_number += 1;
            comment_button.innerHTML = `Comments (${comment_number})`;

            // Add a new comment element to the DOM
            var parent_element = document.querySelectorAll('.post-div')[1];
            var new_comment = document.createElement('div');
            new_comment.className = 'comment-div';
            new_comment.setAttribute('data-comment', data.id);
            new_comment.innerHTML = `<h5><a href="${data.author}" class="post-user">${data.author}</a></h5>`;
            new_comment.innerHTML += `<button type="button" class="btn btn-outline-warning">Edit</button>`;
            if (data.thumb) {
                new_comment.innerHTML += `<img class="post-img" src=${data.thumb}>`;
            }
            new_comment.innerHTML += `<p class="post-content">${data.content}</p>`;
            new_comment.innerHTML += `<p class="post-timestamp">${data.timestamp}</p>`;
            new_comment.innerHTML += `<button class="btn" id="like-button"><i class='far fa-thumbs-up' id="like-icon"></i></button>`;

            // Setting the margin of the like count does not work without specifying it 
            // in JavaScript. Added a style attribute here to fix this issue
            new_comment.innerHTML += `<p class="post-likecount" style="margin-left: 6.5px">0</p>`;
            new_comment.innerHTML += `<hr>`;
            parent_element.insertBefore(new_comment, parent_element.children[6]);
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}
    

// Updates a user's likes and updates the DOM when 
// the user likes a post or comment   
function like_item(item) {
    
    // Store the item ID and viewer's username for 
    // requests. Also create a boolean that indicates whether the 
    // viewer has liked the item and store the user API route
    var item_id;
    if (item.className === 'post-div') {
        item_id = parseInt(item.dataset["post"]);
    }
    else if (item.className === 'comment-div') {
        item_id = parseInt(item.dataset["comment"]);
    }
    const viewer_name = document.querySelector('.posts-page').dataset["viewer"];
    var already_liked = false;
    const user_api_route = `/forum/${viewer_name}`;

    // Make a GET request to the username's route to see
    // if the user has liked the post or comment
    fetch(user_api_route)

    // Convert response to JSON data
    .then(response => response.json())

    // Update the boolean variable if the user has
    // already liked the post or comment
    .then(user => {
        user.likes.forEach(function(liked_post) {
            if (liked_post.id == item_id) {
                already_liked = true;
            }
        }); 

        // Send a PUT request to the viewer's route
        return fetch(user_api_route, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: 'PUT',
            body: JSON.stringify({
                post_id: item_id
            })
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
