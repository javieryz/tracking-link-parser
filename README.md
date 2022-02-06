# tracking-link-parser
This Python script retrieves orders' tracking links sent to the user and sends them via WhatsApp.

## How it works
The app gains access to the user's emails using Google's Gmail API. After the user has given permission to the app, it retrieves a list of emails that match a certain query string. Given the purpose of the application, I chose to get emails sent in the last 24 hours containing the word 'track'. After converting the emails' bytes to readable text, it stores all the content in a single .txt file. Then, it performs a search using regular expressions to detect HTML anchor links containing UPS or DHL tracking links (those are the two couriers I personally use the most, but you could add more as long as you know the URL they use). Lastly, it sends those links using Twilio's WhatsApp API.
