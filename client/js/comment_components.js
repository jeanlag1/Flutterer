/**
 * File: comment_components.js
 * ---------------------------
 * Contains component construction functions that have to do with creating DOM
 * representations of comments, and groups of comments.
 */
"use strict";

/**
 * Component: CommentList
 * ----------------------
 * Generates a div displaying all the comments on a particular floot.
 *
 * Parameters:
 *   * floot: Aggregate containing info about the floot you want to show
 *     comments for
 *   * loggedInUsername: Username of logged-in user (string)
 *   * actions: Aggregate containing a function that can be used to delete a
 *     comment
 *
 * Returns a node with the following structure:
 *   <div class="comment-list">
 *       {{#for comment in floot.comments}}
 *           <Comment />
 *       {{/for}}
 *   </div>
 */
function CommentList(floot, loggedInUsername, actions) {
    let container = document.createElement("div");
    container.classList.add("comment-list");

    for (let commentID of Object.keys(floot.comments)) {
        let comment = floot.comments[commentID];
        container.appendChild(Comment(comment.id, comment.username, comment.message,
            /* showDelete = */ loggedInUsername === comment.username, floot.id, actions));
    }

    return container;
}

/**
 * Component: Comment
 * ------------------
 * Generates a "div" representing a comment on the screen, containing the
 * poster's profile photo and name, and the contents of the comment.
 *
 * Parameters:
 *   * id: Comment ID (string)
 *   * name: Username of comment author (string)
 *   * message: Contents of comment (string)
 *   * showDelete: Whether the "delete" button should be displayed (boolean)
 *   * flootId: ID of the floot that this comment belongs to (string)
 *   * actions: Aggregate containing a function that can be used to delete this
 *     comment
 *
 * Returns a node with the following structure:
 *   <div class="comment">
 *       {{#if showDelete}}
 *           <DeleteButton />
 *       {{/if}}
 *       <ProfilePicture />
 *       <CommentContents />
 *   </div>
 */
function Comment(id, name, message, showDelete, flootId, actions) {
    let container = document.createElement("div");
    container.classList.add("comment");

    if (showDelete) {
        container.appendChild(DeleteButton(deleteComment));
    }
    container.appendChild(ProfilePicture(name, "img/" + name + ".jpg"));
    container.appendChild(CommentContents(name, message));

    function deleteComment() {
      actions.deleteComment(flootId, id, name, actions);
        // TODO: Milestone 8: Use one of your functions in `actions` to delete
        // this comment.
    }

    return container;
}

/**
 * Component: CommentContents
 * --------------------------
 * Generates a simple div containing the name of the commenter and the text of
 * the comment.
 *
 * Parameters:
 *   * name: Username of comment author (string)
 *   * message: Contents of the comment (string)
 *
 * Returns a node with the following structure:
 *   <div>
 *       <div class="user">
 *           {{ name }}
 *       </div>
 *       <div class="comment-content">
 *           {{ message }}
 *       </div>
 *   </div>
 */
function CommentContents(name, message) {
    let container = document.createElement("div");

    let posterContainer = document.createElement("div");
    posterContainer.classList.add("user");
    posterContainer.appendChild(document.createTextNode(name));
    container.appendChild(posterContainer);

    let commentContainer = document.createElement("div");
    commentContainer.classList.add("comment-content");
    commentContainer.appendChild(document.createTextNode(message));
    container.appendChild(commentContainer);

    return container;
}

/**
 * Component: NewCommentEntry
 * --------------------------
 * Creates a text box and a submit button for adding new comments to floots.
 *
 * Parameters:
 *   * floot: An aggregate/object containing information about the floot that
 *     is being commented on
 *   * actions: An aggregate containing a function that can be used to submit a
 *     new comment
 *
 * Returns a node with the following structure:
 *   <div>
 *       <textarea class="new-comment-text" placeholder="Add Comment" />
 *       <button class="button new-comment-btn">Add Comment</button>
 *   </div>
 */
function NewCommentEntry(user, floot, actions) {
    let container = document.createElement("div");

    let textbox = document.createElement("textarea");
    textbox.classList.add("new-comment-text");
    textbox.setAttribute("placeholder", "Add Comment");
    container.appendChild(textbox);

    let button = document.createElement("button");
    button.appendChild(document.createTextNode("Add Comment"));
    button.classList.add("button");
    button.classList.add("new-comment-btn");
    button.addEventListener("click", submitComment);
    container.appendChild(button);


    function submitComment() {
      actions.createComment(floot.id, textbox.value, user, actions);
        // TODO: Milestone 8: Use one of your functions in `actions` to post
        // this new comment.
    }

    return container;
}
