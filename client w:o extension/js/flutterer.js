/**
 * File: flutterer.js
 * ------------------
 * Contains the logic that makes Flutterer work, as well as all initialization.
 */
"use strict";

// Specify a list of valid users. (Extension opportunity: You can create an
// API route that lets users sign up, and then here, you can load a list of
// registered users.)
const USERS = [
    "Suzanne Joh",
    "Ryan Eberhardt",
    "Anand Shankar",
    "Jonathan Kula",
    "Esteban Rey",
];

/**
 * Function: Flutterer
 * -------------------
 * Flutterer's entry point
 */
function Flutterer() {
  let req = AsyncRequest("/api/floots");
  req.setSuccessHandler(function(response){
    let floots = JSON.parse(response.getPayload());
    let actions = {
      switchUser : function(user_switched_to) {
        GetApiFlootsAndReRender(user_switched_to, actions, null);
      },
      createFloot : function(message, username) {
        let reqpost1 = AsyncRequest("/api/floots");
        reqpost1.setMethod("POST");
        reqpost1.setPayload(JSON.stringify({
          username : username,
          message : message,
        }));
        reqpost1.setSuccessHandler(function(){
          GetApiFlootsAndReRender(username, actions, null);
        });
        reqpost1.send();
      },
      deleteFloot : function(floot_id, username){
        let reqpost2 = AsyncRequest("/api/floots/" + floot_id + "/delete");
        reqpost2.setMethod("POST");
        reqpost2.setPayload(JSON.stringify({
          username : username,
        }));
        reqpost2.setSuccessHandler(function(){
          GetApiFlootsAndReRender(username, actions, null);
        });
        reqpost2.send();
      },
      openFlootInModal : function(username, actions, flootObject){
        GetApiFlootsAndReRender(username, actions, flootObject);
      },
      closeModal : function(username, actions){
        GetApiFlootsAndReRender(username, actions, null);
      },
      createComment : function(floot_id, message, username, actions){
        let reqpost3 = AsyncRequest("/api/floots/" + floot_id + "/comments");
        reqpost3.setMethod("POST");
        reqpost3.setPayload(JSON.stringify({
          username : username,
          message : message,
        }));
        reqpost3.setSuccessHandler(function(){
          let reqget = AsyncRequest("/api/floots/" + floot_id);
          reqget.setSuccessHandler(function(response){
            let flootPayload = JSON.parse(response.getPayload());
            actions.openFlootInModal(username, actions, flootPayload);
          });
          reqget.send();
        });
        reqpost3.send();
      },
      deleteComment : function(floot_id, comment_id, username, actions){
        let reqpost4 = AsyncRequest("/api/floots/" + floot_id + "/comments/" + comment_id + "/delete");
        reqpost4.setMethod("POST");
        reqpost4.setPayload(JSON.stringify({
          username : username,
        }));
        reqpost4.setSuccessHandler(function(){
          let reqget = AsyncRequest("/api/floots/" + floot_id);
          reqget.setSuccessHandler(function(response){
            let flootPayload = JSON.parse(response.getPayload());
            actions.openFlootInModal(username, actions, flootPayload);
          });
          reqget.send();
        });
        reqpost4.send();
      },
    };
    document.body.appendChild(MainComponent(USERS[0], floots, actions, null));
  });
  req.send();

  function reRenderMainComponent(user, response, actions, selectedFloot){
    let floots = JSON.parse(response.getPayload());
    while (document.body.lastChild !== null){
      document.body.removeChild(document.body.lastChild);
    }
    document.body.appendChild(MainComponent(user, floots, actions, selectedFloot));
  }
  function GetApiFlootsAndReRender(user, actions, selectedFloot){
    let request = AsyncRequest("/api/floots");
    request.setSuccessHandler(function(response){
        reRenderMainComponent(user, response, actions, selectedFloot);
    })
    request.send();
  }
    // TODO: Implement this function, starting in Milestone 2
}

/**
 * Component: MainComponent
 * ------------------------
 * Constructs all the elements that make up the page.
 *
 * Parameters:
 *   * selectedUser: username of the logged-in user (string)
 *   * floots: an array of floot aggregates/objects that make up the news feed
 *   * actions: an aggregate containing a variety of functions that can be used
 *     to change the page or send data to the server (e.g. change the currently
 *     logged-in user, delete floots, etc.)
 *   * TODO: In Milestone 7: a parameter that contains the floot object that
 *     should be displayed in a modal, or null if no floot has been clicked and
 *     the modal should not be displayed
 *
 * Returns a node with the following structure:
 *   <div class="primary-container">
 *       <Sidebar />
 *       <NewsFeed />
 *   </div>
 */
function MainComponent(selectedUser, floots, actions, selectedFloot) {
  let container = document.createElement("div");
  container.classList.add("primary-container");
  container.appendChild(Sidebar(USERS, selectedUser, actions));
  container.appendChild(NewsFeed(selectedUser, floots, actions));
  if (selectedFloot != null){
    container.appendChild(FlootModal(selectedFloot, selectedUser, actions));
  }
  return container;
    // TODO: Implement this component in Milestone 2
}

/**
 * NOTE TO STUDENTS: you don't need to understand anything below.  It's fancy
 * JavaScript we need to help make the development process a little easier.
 *
 * The following code uses some Javascript magic so that all network requests
 * are logged to the browser console. You can still view all network requests
 * in the Network tab of the browser console, and that may be more helpful (it
 * provides much more useful information), but students may find this handy for
 * doing quick debugging.
 */
(() => {
    function log_info(msg, ...extraArgs) {
        console.info("%c" + msg, "color: #8621eb", ...extraArgs);
    }
    function log_success(msg, ...extraArgs) {
        console.info("%c" + msg, "color: #39b80b", ...extraArgs);
    }
    function log_error(msg, ...extraArgs) {
        console.warn("%c" + msg, "color: #c73518", ...extraArgs);
    }
    const _fetch = window.fetch;
    window.fetch = function(...args) {
        log_info(`Making async request to ${args[1].method} ${args[0]}...`);
        return new Promise((resolve, reject) => {
            _fetch(...args).then((result) => {
                const our_result = result.clone();
                our_result.text().then((out_text) => {
                    if (our_result.ok) {
                        log_success(`Server returned successful response for ${our_result.url}`);
                    } else {
                        log_error(`Server returned Error ${our_result.status} `
                            + `(${our_result.statusText}) for ${our_result.url}`,
                            out_text);
                    }
                    resolve(result);
                });
            }, (error) => {
                log_error('Error!', error);
                reject(error);
            });
        });
    };

    log_info("Did you know?", "For this assignment, we have added some code that "
        + "logs network requests in the JS console. However, the Network tab "
        + "has even more useful information. If you are having problems with API "
        + "calls, the Network tab may be a good place to check out; you can see "
        + "POST request bodies, full server responses, and anything else you might "
        + "desire there.");
})();

document.addEventListener("DOMContentLoaded", Flutterer);
