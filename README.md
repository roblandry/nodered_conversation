# localai-nodered
Custom Component for Home Assistant.  
This creates a NodeRed Conversation Agent (modified from openai conversation agent).  
This will send a conversation to and from nodered to be used with LocalAI or OpenAI.
This is not setup for HACS yet.

## Note: This is very early beta and subject to breaking. Anyone want to help clean up or make better, I am happy for the assistance.
ToDo:  
- [ ]  Errors should be red.
- [ ]  Fix Config Flow/Options. (note: options current do nothing. config flow is where everything is set)
- [ ]  Other things I'm missing...

## Install
*  Load the custom component into home assistant
*  Restart home assistant
*  Add the NodeRed Conversation integration
  add the url for nodered. should be something like https://192.168.1.1:1880/endpoint/gpt. add a username and password to be used in the node red flow.
*  Select the new Conversation agent. Settings>Voice Assistants>Home Assistant>Conversation agent.
*  Copy the nodered_sample_flow.json and import into node red.
*  Make sure you change the username and password in the auth node
*  For OpenAI: (not tested) You will need to enter you api key for open ai and remove the line for url
*  For localAI: api key doesnt matter. But you will need to add the url or ip address to your server.

*  Profit