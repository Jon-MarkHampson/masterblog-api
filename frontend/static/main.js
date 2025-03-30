// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `
                <h2>${post.title}</h2>
                <p>${post.content}</p>
                <p>Author: ${post.author}</p>
                <p>Date: ${post.date}</p>
                <div class="buttons-wrapper">
                <button class="post-like" onclick="likePost(${post.id})">Like ${post.likes}</button>
                <button class="post-update" onclick="updatePost(event, ${post.id})">Update</button>
                <button class="post-delete" onclick="deletePost(${post.id})">Delete</button>
                </div>`;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date').value;
    
    // Validate the input fields
    if (!postTitle || !postContent || !postAuthor || !postDate) {
        alert('Please fill in all fields.');
        return;
    }
    
    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: postTitle,
            content: postContent,
            author: postAuthor,
            date: postDate
        })
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post added:', post);
        // Clear the input fields, allowing the placeholder text to show again
        document.getElementById('post-title').value = "";
        document.getElementById('post-content').value = "";
        document.getElementById('post-author').value = "";
        document.getElementById('post-date').value = "";
        
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Function to like a post
function likePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId + '/like', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Post liked:', data);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

function updatePost(event, postId) {
    // Get the post container by using the closest element with class 'post'
    var postDiv = event.target.closest('.post');
    
    // Retrieve the current title, content, author, and date from the post display
    var currentTitle = postDiv.querySelector('h2').innerText;
    var paragraphs = postDiv.querySelectorAll('p');
    var currentContent = paragraphs[0].innerText;
    var currentAuthor = paragraphs[1].innerText.replace("Author: ", "");
    var currentDate = paragraphs[2].innerText.replace("Date: ", "");

    // Replace the post content with an editable form
    postDiv.innerHTML = `
        <div class="post-edit">
        <input type="text" id="edit-title-${postId}" value="${currentTitle}">
        <textarea id="edit-content-${postId}">${currentContent}</textarea>
        <input type="text" id="edit-author-${postId}" value="${currentAuthor}">
        <input type="text" id="edit-date-${postId}" value="${currentDate}">
        <button class="save-button" onclick="saveUpdatedPost(${postId})">Save</button>
        <button onclick="loadPosts()">Cancel</button>
        </div>
    `;
}

function saveUpdatedPost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;
    var updatedTitle = document.getElementById(`edit-title-${postId}`).value;
    var updatedContent = document.getElementById(`edit-content-${postId}`).value;
    var updatedAuthor = document.getElementById(`edit-author-${postId}`).value;
    var updatedDate = document.getElementById(`edit-date-${postId}`).value;

    // Use the Fetch API to send a PUT request with the updated post data
    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            title: updatedTitle, 
            content: updatedContent, 
            author: updatedAuthor, 
            date: updatedDate 
        })
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post updated:', post);
        loadPosts(); // Reload the posts to reflect the updated posts.json
    })
    .catch(error => console.error('Error:', error));
}