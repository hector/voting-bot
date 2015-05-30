// Configuration values

var url = 'http://www.example.com/poll';
var optionId = 'option-id'
var voteFunction = function() {
  // JS code to trigger voting
  vote();
};
var waitForVote = function() {
  // JS code that will return true once voting is finished
  return document.getElementById('voteFeedback') != null;
};

// END Configuration values

/**
 * Wait until the test condition is true or a timeout occurs. Useful for waiting
 * on a server response or for a ui change (fadeIn, etc.) to occur.
 *
 * @param testFx javascript condition that evaluates to a boolean,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param onReady what to do when testFx condition is fulfilled,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param timeOutMillis the max amount of time to wait. If not specified, 3 sec is used.
 */
function waitFor(testFx, onReady, timeOutMillis) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3000, //< Default Max Timout is 3s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    console.log("'waitFor()' timeout");
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    console.log("'waitFor()' finished in " + (new Date().getTime() - start) + "ms.");
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 250); //< repeat check every 250ms
};


var page = require('webpage').create();
page.settings.javascriptEnabled = true;
page.settings.loadImages = false;
page.settings.webSecurityEnabled = false;
page.settings.resourceTimeout = 10000;

// Route web console messages to output
page.onConsoleMessage = function(msg) {
    console.log(msg);
};

page.open(url, function(status) {
  console.log("Status: " + status);
  
  console.log('Selecting option...');
  page.evaluate(function () {
    var a = document.getElementById(optionId);
    var e = document.createEvent('MouseEvents');
    e.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
    a.dispatchEvent(e);
    waitforload = true;
  });
  console.log('Selected');
  
  console.log('Voting...');
  page.evaluate(voteFunction());

  waitFor(function() {
    return page.evaluate(waitForVote);
  }, function() {
      console.log('Voted');
      phantom.exit();      
  }, 10000);
});
