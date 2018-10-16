display notification with title "Zendesk Talk availability" subtitle "Set to phone"
do shell script "#!/bin/sh
#Your Zendesk URL has two parts: a subdomain name you chose when you set up your account, followed by zendesk.com (for example: mycompany.zendesk.com).
#Your Zendesk User ID is found in Agent Profile URL.
#Requires Zendesk API Token Access
#Add Activate API Token to Keychain as a new Password item, set account name to your $zendeskUsername + '/token', e.g. 'sue@example.com/token'.
#####
#Enter your credentials here:
zendeskSubdomain=
zendeskUserID=
zendeskUsername=
get_pw () {
security 2>&1 >/dev/null find-generic-password -ga $zendeskUsername/token|ruby -e 'print $1 if STDIN.gets =~ /^password: \"(.*)\"$/'
}
curl https://$zendeskSubdomain.zendesk.com/api/v2/channels/voice/availabilities/$zendeskUserID.json -H \"Content-Type: application/json\" -d '{\"availability\": {\"via\": \"phone\", \"available\": true}}' -v -u $zendeskUsername/token:$(get_pw) -X PUT"