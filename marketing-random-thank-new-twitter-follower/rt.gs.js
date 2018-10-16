function rt() {
  // Optional: set ID of spreadsheet, otherwise assume script is sheet-bound, and open the active spreadsheet.
  var ss = (optSSId) ? SpreadsheetApp.openById(optSSId) : SpreadsheetApp.getActiveSpreadsheet();
  var optSSId = '1UWlcYV1Je3N2gtIl1Z0Y8x0uIFoPj5LWPlc9nvd5WoA'; 
  var sheet = ss.getSheets()[0];
  // the data range with column headers: Twitter handle, Name, Followed me, Location
  var rangeFollowers = sheet.getDataRange(); 
  var valuesFollowers = rangeFollowers.getValues();
  var greetingsArray = [
    "👋",
    "Hi",
    "Yo",
    "Hey",
    "Dear",
    "Hello",
    "G'day",
    "Howdy",
    "Shout out to",
    "Aloha",
    "As-Salamualaikum",
    "Shalom",
    "Namaste",
    "Ciao",
    "Welcome",
    "🤝",
    "🙇‍♂️"
  ];
  var thanksArray = [
    "🙏 for the follow!",
    "Thanks for the follow!",
    "Thanks for the follow, all the best.",
    "Thanks for the follow. You're the best.",
    "Thanks for the follow. Have a good one!",
    "Pleased to meet you. Look a double rainbow, Woah! 🌈🌈 ",
    "Thanks for the follow! Hope to learn from your tweets.",
    "Have some 🍨 on me. If you’re lactose intolerant, it’s dairy free. 👍",
    "What brought you to follow @itsolvernet?",
    "If you would like free advice on setting up technology in your home or business, check out our blog: itsolver.net/blog",
    "Want to see what kind of articles I write? Visit my blog: itsolver.net/blog",
    "Want to learn more about technology in your home and business, visit: itsolver.net/blog",
    "It means a lot to me that you're interested in my business.",
    "Subscribe to free technology advice: eepurl.com/bMD5GX",
    "If you want to learn more about tech (jargon free), sign up for our newsletter: eepurl.com/bMD5GX",
    "If you want jargon free advice on everyday technology, sign up for our newsletter: eepurl.com/bMD5GX",
    "Sign up for our newsletter: eepurl.com/bMD5GX",
    "Get more out of your technology. Visit itsolver.net/blog",
    "I'm going to spend the next 5 minutes seeing how I can help your mission",
    "Is there anything we can do to help achieve your life goals?",
    "What challenges are you facing at work or in your business? I'd like to help!",
    "Help is here.",
    "Business technology made simple: itsolver.net",
    "Want tech support with anything Google, Apple or Microsoft?",
    "We provide tech support for all major Home Entertainment brands including Apple, LG, Samsung, Sony, Sonos and more.",
    "Do business better with IT Solver - itsolver.net",
    "Work smarter with IT Solver.",
    "Would you like a free technology audit? You might be surprised what you can do with IT Solver",
    "Want a free technology audit? You might be surprised what you're capabable of with advice from IT Solver.",
    "The purpose of IT Solver is to have a positive impact on as many people as possible. Have a wonderful day!",
    "Have a tremendous day.",
    "You are the best.",
    "What's a favourite app on your home screen?"
  ];
  if (!valuesFollowers) {
    Logger.log('No valuesFollowers data found.');
  } else { // proceed with composing random thank you tweet
    Logger.log('New Followers! Thank them:');
    for (var row = 1; row < valuesFollowers.length; row++) {
      if(valuesFollowers[row][0] == '' || valuesFollowers[row][5] != '') { // do nothing if Follower's ScreenName is undefined or Tweet Text already generated 
        Logger.log ('Skipped: ' + valuesFollowers[row][0] + ',' + valuesFollowers[row][5]);
      } else if (valuesFollowers[row][3] == '') { // if Follower's Location is undefined, compose a simple thank you sentence
        var randomGreeting = Math.floor(Math.random()*greetingsArray.length); // pick a random greeting
        var randomThanks = Math.floor(Math.random()*thanksArray.length); // pick a random thank you comment
        var randomThanksTweet = greetingsArray[randomGreeting] + ' ' + valuesFollowers[row][0] + ' ' + thanksArray[randomThanks];
      } else { // if Follower's Location known, include a sentence about the follower's location
        var locationsArray = [
          "from " + valuesFollowers[row][3] + ".",
          "may all your dreams come true in " + valuesFollowers[row][3] + ".",
          "in " + valuesFollowers[row][3] + ".",
          "in " + valuesFollowers[row][3] + " from Brisbane, Australia 🌏🏝🐨",
          "in #" + valuesFollowers[row][3] + ".",
          "all the way from " + valuesFollowers[row][3] + ".",
          "at " + valuesFollowers[row][3] + ".",
          "being awesome at " + valuesFollowers[row][3] + ".",
          ""
        ]
        var randomGreeting = Math.floor(Math.random()*greetingsArray.length); // pick a random greeting
        var randomThanks = Math.floor(Math.random()*thanksArray.length); // pick a random thank you comment
        var randomLocation = Math.floor(Math.random()*locationsArray.length); // pick a random location comment
        var randomThanksTweet = greetingsArray[randomGreeting] + ' ' + valuesFollowers[row][0] + ' ' + locationsArray[randomLocation] + ' ' + thanksArray[randomThanks]; 
      }
      if((valuesFollowers[row][0] == '') || (valuesFollowers[row][5] != '')) { // do nothing if Follower's ScreenName is undefined or Tweet Text already generated 
      } else {
        var cell = sheet.getRange('F' + (row + 1)); 
        cell.setValue(randomThanksTweet);
      }
    }
    }
  sheet.getRange('B:B').activate();
  sheet.getActiveRangeList().setShowHyperlink(false);
  sheet.getRange('I2').activate();
}

function onEdit(e){
  var rr = e.range;
  var ss = e.range.getSheet();

  var headerRows = 1;  // # header rows to ignore
  var sentRow = 7;     // # column to ignore

  if (rr.getRow() <= headerRows) return;
  if (rr.getColumn() == sentRow) return;

  rt() // generate random thanks
}