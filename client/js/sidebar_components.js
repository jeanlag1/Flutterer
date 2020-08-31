/**
 * File: sidebar_components.js
 * ---------------------------
 * Contains component construction functions that have to do with creating DOM
 * representations for the left sidebar of the page.
 */
"use strict";

/**
 * Component: Sidebar
 * ------------------
 * Generates a div that represents the left sidebar of the page.
 *
 * Parameters:
 *   * users: a list of usernames (i.e. list of strings)
 *   * selectedUser: the username that should be highlighted in the list
 *   * actions: an aggregate containing functions that can be used to set the
 *     current logged-in user
 *
 * Returns a node with the following structure:
 *   <div class="sidebar">
 *       <FluttererLogo />
 *       <AccountSelector />
 *   </div>
 */
function Sidebar(users, selectedUser, actions) {
    let sidebar = document.createElement("div");
    sidebar.classList.add("sidebar");
    sidebar.appendChild(FluttererLogo());
    sidebar.appendChild(AccountSelector(users, selectedUser, actions));
    return sidebar;
}

/**
 * Component: FluttererLogo
 * ------------------------
 * Returns a div containing the logo:
 *
 *   <div class="flutterer-logo">
 *       <img class="owl-icon" alt="Flutterer Logo" src="img/floot-icon.png" />
 *       <span>flutterer</span>
 *   </div>
 */
function FluttererLogo() {
    let logo = document.createElement("div");
    logo.classList.add("flutterer-logo");

    let icon = document.createElement("img");
    icon.classList.add("owl-icon");
    // Set alt text for vision impaired
    icon.setAttribute("alt", "Flutterer Logo");
    icon.setAttribute("src", "img/floot-icon.png");
    logo.appendChild(icon);

    let text = document.createElement("span");
    text.appendChild(document.createTextNode("flutterer"));
    logo.appendChild(text);

    return logo;
}

/**
 * Component: AccountSelector
 * --------------------------
 * Generates a list of buttons (one button per user), with selectedUser
 * highlighted (the "account-clicked" class will be added to that user's
 * button).
 *
 * Parameters:
 *   * users: a list of usernames (i.e. list of strings)
 *   * selectedUser: the username that should be highlighted in the list
 *   * actions: an aggregate containing funtions that can be used to set the
 *     current logged-in user
 *
 * Returns the following structure:
 *   <div class="account-list">
 *       <p class="hint">Log in as:</p>
 *       {{for each user}}
 *       <button class="account">{Username}</button>
 *       {{end for}}
 *   </div>
 */
function AccountSelector(users, selectedUser, actions) {
    let accountList = document.createElement("div");
    accountList.classList.add("account-list");

    let hintText = document.createElement("p");
    hintText.classList.add("hint");
    hintText.appendChild(document.createTextNode("Log in as:"));
    accountList.appendChild(hintText);

    for (let username of users) {
        // Create button and add it to the list
        let button = document.createElement("button");
        button.appendChild(document.createTextNode(username));
        button.classList.add("account");
        if (selectedUser === username) {
            button.classList.add("account-clicked");
        }
        accountList.appendChild(button);

        function buttonClicked() {
          actions.switchUser(username);
            // TODO: Milestone 4: Call one of your functions in `actions` to
            // change the selected user.
        }
        button.addEventListener("click", buttonClicked);
    }

    return accountList;
}
