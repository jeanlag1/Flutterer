/**
 * File: modal_components.js
 * -------------------------
 * Contains component construction functions that have to do with creating DOM
 * representations for modals (i.e. popups that appear within the page).
 */
"use strict";

/**
 * Component: FlootModal
 * ---------------------
 * Displays a pop-up "modal" (kind of like an in-screen pop-up window) that
 * shows a floot's comments, and gives you the option to add a new comment.
 *
 * Parameters:
 *   * floot: the floot aggregate that should be displayed in this modal
 *   * selectedUser: username of the logged-in user (string)
 *   * actions: an aggregate containing functions that can be called in order
 *     to open/close the modal, post comments, etc.
 *
 * Returns a node with the following structure:
 *   <div class="modal">
 *       <div class="modal-content">
 *           <div>
 *               <MaterialIcon icon="close" class="pointer modal-close" />
 *           </div>
 *           <div class="scrollable">
 *               <Floot />
 *               <span class="comments-label">Comments:</span>
 *               <div class="comments-container">
 *                   <CommentList />
 *                   <NewCommentEntry />
 *               </div>
 *           </div>
 *       </div>
 *   </div>
 */
function FlootModal(floot, selectedUser, actions) {
    // Show the clicked floot at the top of the modal (so it's clear what the
    // comments are responding to)
    let selectedFlootNode = Floot(floot, selectedUser, /* showDelete = */ false,
        actions);

    let commentsLabel = document.createElement("span");
    commentsLabel.classList.add("comments-label");
    commentsLabel.appendChild(document.createTextNode("Comments:"));

    let commentsContainer = document.createElement("div");
    commentsContainer.classList.add("comments-container");
    commentsContainer.appendChild(CommentList(floot, selectedUser, actions));
    commentsContainer.appendChild(NewCommentEntry(selectedUser, floot, actions));

    // Put these elements inside a scrollable region (useful if there are too
    // many comments to fit on the screen)
    let scrollable = document.createElement("div");
    scrollable.classList.add("scrollable");
    scrollable.appendChild(selectedFlootNode);
    scrollable.appendChild(commentsLabel);
    scrollable.appendChild(commentsContainer);

    // Create close button
    let closeBtnContainer = document.createElement("div");
    let closeBtn = MaterialIcon("close");
    closeBtn.classList.add("pointer");
    closeBtn.classList.add("modal-close");
    closeBtnContainer.appendChild(closeBtn);
    function closeAction(){
      actions.closeModal(selectedUser, actions);
    }
    closeBtn.addEventListener("click", closeAction);
    // TODO: Milestone 7: Call one of your functions in `actions` to close the
    // modal when closeBtn is clicked.

    // Put content and close button inside modal
    let modalContent = document.createElement("div");
    modalContent.classList.add("modal-content");
    modalContent.appendChild(closeBtnContainer);
    modalContent.appendChild(scrollable);

    // Put the modal inside a container that spans the full screen. (This way,
    // if you click outside the modal border, the modal will close.)
    let modal = document.createElement("div");
    modal.classList.add("modal");
    modal.appendChild(modalContent);
    // Close modal on click outside modal
    modal.addEventListener("click", function (e) {
        // Only handle clicks on the modal background itself. (Otherwise, the
        // modal will close if you click *anything* inside it.)
        if (e.target === modal) {
          actions.closeModal(selectedUser, actions);
            // TODO: Milestone 7: Close the modal.
        }
    });

    return modal;
}
