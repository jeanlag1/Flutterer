/**
 * File: general_components.js
 * ---------------------------
 * Contains component construction functions that have to do with creating DOM
 * representations of elements that are used by many other components.
 */
"use strict";

/**
 * Component: ProfilePicture
 * -------------------------
 * Given a name and an image, creates a profile picture with the following
 * structure:
 *
 * <img src="{{imageUrl}}" alt="User Profile Image for {{name}}" />
 */
function ProfilePicture(name, imageUrl) {
    let image = document.createElement("img");
    image.src = imageUrl;
    image.className = "user-photo";
    image.alt = "User Profile Image for " + name;
    return image;
}

/**
 * Component: LikeCount
 * --------------------
 * Constructs a like counter that displays the number of likes a post has, and
 * communicates whether or not that post was liked by the current user.
 * LikeCount has the following structure:
 *
 * <div class="heart">
 *     {{#if isLiked}}
 *         <MaterialIcon name="favorite" />
 *     {{#else}}
 *         <MaterialIcon name="favorite_border" />
 *     {{/if}}
 *     <span>
 *         {{ numLikes }}
 *     </span>
 * </div>
 */
function LikeCount(numLiked, isLiked) {
    let container = document.createElement("div");
    container.className = "like-count";

    let heart = isLiked ? MaterialIcon("favorite") : MaterialIcon("favorite_border");

    let countSpan = document.createElement("span");
    countSpan.appendChild(document.createTextNode(numLiked));

    container.appendChild(heart);
    container.appendChild(countSpan);
    return container;
}

/**
 * Component: CommentCount
 * -----------------------
 * Constructs a comment counter that displays the number of comments a post
 * has.  CommentCount has the following structure:
 *
 * <div class="comment-count">
 *     <MaterialIcon name="comment" />
 *     <span>
 *         {{ numComments }}
 *     </span>
 * </div>
 */
function CommentCount(numComments) {
    let container = document.createElement("div");
    container.className = "comment-count";

    let countSpan = document.createElement("span");
    countSpan.appendChild(document.createTextNode(numComments));

    container.appendChild(MaterialIcon("comment"));
    container.appendChild(countSpan);

    return container;
}

/**
 * Component: DeleteButton
 * -----------------------
 * Takes a function that should be called when the delete button is clicked.
 * Returns the following node:
 *
 * <MaterialIcon name="delete" />
 *
 * This will display an trash bin icon on the screen, representing a delete
 * button.  When the icon is clicked, onDelete will be called.
 */
function DeleteButton(onDelete) {
    let button = MaterialIcon("delete");
    button.classList.add("pointer");
    button.classList.add("delete-btn");

    function handleClick(e) {
        onDelete();
        e.stopPropagation();
    }
    button.addEventListener("click", handleClick);

    return button;
}

/**
 * Component: MaterialIcon
 * -----------------------
 * Given a name of a material icon, returns an element that displays that icon.
 * This has the following structure:
 *
 * <i class="material-icons">{{name}}</i>
 *
 * NOTE TO STUDENTS: You probably won't need to use this. However, if you're
 * doing an extension and want to add a new icon, you can find a list of all
 * icon names here: https://material.io/resources/icons/?style=baseline
 */
function MaterialIcon(name) {
    let icon = document.createElement("i");
    icon.classList.add("material-icons");
    icon.appendChild(document.createTextNode(name));
    return icon;
}

