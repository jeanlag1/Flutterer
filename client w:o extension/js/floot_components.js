/**
 * File: floot_components.js
 * -------------------------
 * Contains component construction functions that have to do with creating DOM
 * representations of floots, and groups of floots.
 */
"use strict";

/**
 * Component: NewsFeed
 * -------------------
 * Generates the elements needed to display the right side of the screen (the
 * "new floot" text box, and, below it, the list of floots that have been
 * posted).
 *
 * Parameters:
 *   * selectedUser: the currently logged-in username (string)
 *   * floots: an array of floot aggregates to show in the feed
 *   * actions: an aggregate containing functions that can be used to open a
 *     modal, post a new floot, etc
 *
 * Returns the following structure:
 *   <div class="newsfeed">
 *       <NewFlootEntry />
 *       <FlootList />
 *   </div>
 *
 * You don't need to change anything here.
 */
function NewsFeed(selectedUser, floots, actions) {
    let newsfeed = document.createElement("div");
    newsfeed.classList.add("newsfeed");

    // Add text box for creating new floots. Pass triggerDataRefresh as the
    // second argument to NewFlootEntry, so that it can be called when the
    // "Floot" button is pressed (in order to refresh the floot list and
    // display the newly-posted floot).
    newsfeed.appendChild(NewFlootEntry(selectedUser, actions));

    // Show list of floots on the page. When a floot is deleted or liked,
    // triggerDataRefresh will be called.
    newsfeed.appendChild(FlootList(floots, selectedUser, actions));

    return newsfeed;
}


/**
 * Component: NewFlootEntry
 * ------------------------
 * Creates the interface for posting new floots (a textbox and a "Floot"
 * button). When the "Floot" button is clicked, a function in `actions` will be
 * called to send the new floot to the server.
 *
 * Parameters:
 *   * selectedUser: Username of the logged-in user (string)
 *   * actions: An aggregate containing a function that can be used to create a
 *     new floot
 *
 * Returns a node with the following structure:
 *   <div class="new-floot-entry">
 *       <ProfilePicture />
 *       <textarea placeholder="What's fluttering?" />
 *       <button class="button floot-button">Floot</button>
 *   </div>
 */
function NewFlootEntry(selectedUser, actions) {
    let container = document.createElement("div");
    container.classList.add("new-floot-entry");

    let profilePic = ProfilePicture(selectedUser, "img/" + selectedUser + ".jpg");
    container.appendChild(profilePic);

    let textbox = document.createElement("textarea");
    textbox.setAttribute("placeholder", "What's fluttering?");
    container.appendChild(textbox);

    let flootButton = document.createElement("button");
    flootButton.classList.add("button");
    flootButton.classList.add("floot-button");
    flootButton.appendChild(document.createTextNode("Floot"));
    flootButton.addEventListener("click", postFloot);
    container.appendChild(flootButton);

    function postFloot() {
      actions.createFloot(textbox.value, selectedUser);
        // TODO: Milestone 5: Call one of your functions in `actions` to post
        // this floot.
    }

    return container;
}

/**
 * Component: FlootList
 * --------------------
 * Creates a div that has a bunch of "cards" in it that display the floots in
 * the news feed.
 *
 * Parameters:
 *   * floots: an array of floot aggregates/objects
 *   * selectedUser: the currently logged-in user (string)
 *   * actions: an aggregate containing functions that can be used to open a
 *     floot in a modal, delete a floot, like/unlike a floot, etc.
 *
 * Returns a node with the following structure:
 *   <div class="floot-list">
 *       {{#for floot in floots}}
 *           <Floot />
 *       {{/for}}
 *   </div>
 */
function FlootList(floots, selectedUser, actions) {
    let container = document.createElement("div");
    container.classList.add("floot-list");
    for (let floot of floots) {
        let comp = Floot(floot, selectedUser,
            /* showDelete = */ floot.username === selectedUser, actions);

        container.appendChild(comp);
    }
    return container;
}

/**
 * Component: Floot
 * ----------------
 * Produces a "card" representing a floot on the screen. Each card shows the
 * poster's name, profile picture, and the contents of the floot. In addition,
 * there is a like count and comment count displayed in the bottom left, and,
 * if the currently logged-in user is the one that posted the floot, a "delete"
 * button in the top right.
 *
 * When the floot card is clicked, the provided openFlootInModal function will
 * be called (with the purpose of opening the floot in the modal to show its
 * comments). When the delete button is clicked, triggerDataRefresh will be
 * called (in order to refresh the news feed and ensure the Floot disappears
 * from the screen).
 *
 * Parameters:
 *   * flootInfo: a floot object/aggregate, corresponding to the dictionary
 *     returned by the server for a Floot
 *   * selectedUser: the currently logged-in username (string)
 *   * showDelete: boolean (true/false) indicating whether the "delete" button
 *     should be displayed
 *   * actions: an aggregate containing functions that can be used to open a
 *     floot in a modal, delete a floot, like/unlike a floot, etc.
 *
 * Returns a node with the following structure:
 *   <div class="card floot-card">
 *       {{#if showDelete}}
 *           <DeleteButton />
 *       {{/if}}
 *       <ProfilePicture />
 *       <FlootContent />
 *       <LikeCommentCount />
 *   </div>
 */
function Floot(flootInfo, selectedUser, showDelete, actions) {
    let card = document.createElement("div");
    card.classList.add("card");
    card.classList.add("floot-card");

    if (showDelete) {
        card.appendChild(DeleteButton(deleteFloot));
    }
    card.appendChild(ProfilePicture(flootInfo.username, "img/" + flootInfo.username + ".jpg"));
    card.appendChild(FlootContent(flootInfo.username, flootInfo.message));
    card.appendChild(LikeCommentCount(flootInfo, selectedUser, toggleLike));
    card.addEventListener("click", handleCardClick);

    /**
     * Handle clicks on the Floot card. (Open the modal to display this floot's
     * comments.)
     */
    function handleCardClick() {
      actions.openFlootInModal(selectedUser, actions, flootInfo);
        // TODO: Milestone 7: Call one of your functions in `actions` to open a
        // modal showing this floot's comments.
    }

    /**
     * Handle clicks on the delete button.
     */
    function deleteFloot() {
      actions.deleteFloot(flootInfo.id, selectedUser);
        // TODO: Milestone 6: Call one of your functions in `actions` to delete
        // this floot.
    }

    /**
     * Handles clicks on the like button. If the floot is already liked,
     * un-like it; if it is not liked, like it.
     */
    function toggleLike(e) {
        // Stop modal from opening. (If you don't have this, the click event
        // will also be given to the card's click handler, so handleCardClick()
        // will be called and the modal will be opened.)
        e.stopPropagation();

        // TODO: If you are implementing the "like button" extension, call one
        // of your functions in `actions` to like or un-like this floot.
    }

    return card;
}

/**
 * Component: FlootContent
 * -----------------------
 * Creates a simple div that contains the name of the poster and the message of
 * the floot. (This component is necessary so that the name and message can be
 * displayed as one unit to the right of the photo. If you didn't have this
 * container, you would need to arrange the photo, name, and message
 * horizontally, which would look weird because the message would be to the
 * right of the name, or vertically, which would look weird because the photo
 * would be above the name. If you don't understand this, don't worry; it's
 * more of a CSS thing and isn't important for this assignment.)
 *
 * Parameters:
 *   * name: Username of the poster (string)
 *   * message: Contents of the floot (string)
 *
 * Returns a node with the following structure:
 *   <div>
 *       <div class="user">
 *           {{ name }}
 *       </div>
 *       <div>
 *           {{ message }}
 *       </div>
 *   </div>
 */
function FlootContent(name, message) {
    let container = document.createElement("div");

    let userContainer = document.createElement("div");
    userContainer.appendChild(document.createTextNode(name));
    userContainer.classList.add("user");

    let messageContainer = document.createElement("div");
    messageContainer.appendChild(document.createTextNode(message));

    container.appendChild(userContainer);
    container.appendChild(messageContainer);

    return container;
}

/**
 * Component: LikeCommentCount
 * ---------------------------
 * Creates a simple div, positioned in the bottom right of each post,
 * containing the comment count, like button, and like count.
 *
 * Parameters:
 *   * flootInfo: An object/aggregate containing a floot's information (in
 *     particular, a "liked_by" list containing usernames, and a "comments"
 *     list containing comment objects).
 *   * selectedUser: The username of the logged-in user (a string)
 *   * onLike: A function that should be called when the like button is clicked
 *
 * Returns a node with the following structure:
 *   <div class="comment-like-count">
 *       <LikeCount />
 *       <CommentCount />
 *   </div>
 */
function LikeCommentCount(flootInfo, selectedUser, onLike) {
    let container = document.createElement("div");
    container.classList.add("comment-like-count");

    // TODO: if you are implementing the like button extension, append a
    // LikeCount component here. You should also add a click listener to the
    // LikeCount node, calling onLike() when the element is clicked.
    // We haven't learned this in class, but you can do
    // Object.keys(someAggregate) to get an array of keys in that aggregate,
    // and then we can take the array length.
    let numComments = Object.keys(flootInfo.comments).length;
    container.appendChild(CommentCount(numComments));

    return container;
}
