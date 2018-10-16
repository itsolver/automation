var greetingsArray = [
    "Hi",
    "Hey",
    "G'day",
    "Hello",
    "Dear",
    "👋",
    "Yo",
    "Howdy",
]
var thanksArray = [
    "Thanks for the follow!",
    "Thanks for the follower, all the best.",
    "Thanks for the follow. Have a good one!",
    "Thanks for the follow. You're the best.",
    "🙏 for the follow!",
    "Have some 🍨 on me. If you’re lactose intolerant, it’s dairy free. 👍",
    "Thanks for the follow! Hope to learn from your tweets."
];
var randomNumber = Math.floor(Math.random()*thanksArray.length);

if(!inputData.followerLocation) { // compose the random thank you
    var randomthanks = greetingsArray[randomNumber] + " @" + inputData.followerScreenName + " " + thanksArray[randomNumber];
} else { // if follower's location known, include a sentence about the location
    var locationsArray = [
        " from " + inputData.followerLocation + ".",
        ", may all your dreams come true in " + inputData.followerLocation + ".",
        " in " + inputData.followerLocation + ".",
        "" // sometimes, don't mention location
    ]
    var randomNumber = Math.floor(Math.random()*thanksArray.length);
    var randomthanks = greetingsArray[randomNumber] + " @" + inputData.followerScreenName + locationsArray[randomNumber] + " " + thanksArray[randomNumber]; 
}
return output = {'randomthanks': randomthanks};