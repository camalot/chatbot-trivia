# CHATBOT TRIVIA OVERLAY
[![Trivia Overlay](https://github.com/camalot/chatbot-trivia/actions/workflows/build.yml/badge.svg)](https://github.com/camalot/chatbot-trivia/actions/workflows/build.yml)

Creates a trivia overlay and in chat to interact with chat.

[![See Trivia Overlay In Action](https://img.youtube.com/vi/_TgZ5OJOTjc/0.jpg)](https://www.youtube.com/watch?v=_TgZ5OJOTjc)


## REQUIREMENTS

- Install [StreamLabs Chatbot](https://streamlabs.com/chatbot)
- [Enable Scripts in StreamLabs Chatbot](https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts)
- [Microsoft .NET Framework 4.7.2 Runtime](https://dotnet.microsoft.com/download/dotnet-framework/net472) or later

## INSTALL

- Download the latest zip file from [Releases](https://github.com/camalot/chatbot-trivia/releases/latest)
- Right-click on the downloaded zip file and choose `Properties`
- Click on `Unblock`  
[![](https://i.imgur.com/vehSSn7l.png)](https://i.imgur.com/vehSSn7.png)  
  > **NOTE:** If you do not see `Unblock`, the file is already unblocked.
- In Chatbot, Click on the import icon on the scripts tab.  
  ![](https://i.imgur.com/16JjCvR.png)
- Select the downloaded zip file
- Right click on `Trivia Overlay` row and select `Insert API Key`. Click yes on the dialog.  
[![](https://i.imgur.com/AWmtHKFl.png)](https://i.imgur.com/AWmtHKF.png)  

## CONFIGURATION

Make sure the script is enabled  
[![](https://i.imgur.com/2jzqA4Hl.png)](https://i.imgur.com/2jzqA4H.png)  

Click on the script in the list to bring up the configuration.

### COMMAND SETTINGS  
[![](https://i.imgur.com/fXXteDBl.png)](https://i.imgur.com/fXXteDB.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Command` | The command to start a new trivia question | `!trivia` |
| `Cooldown` | The cooldown in seconds for the command. | `30` | 
| `Answer Command` | The command to answer a question. | `!trivia` |
| `Time to Answer` | The time allowed to answer the question. | `60` |
| `OPEN OVERLAY IN BROWSER` | Opens the overlay in your browser. |  |
| `START QUESTION` | Start a new trivia question. |  |
| `CLEAR QUESTION` | Clear the currently active question. |  |


### RESPONSES 

[![](https://i.imgur.com/qY2TT5pl.png)](https://i.imgur.com/qY2TT5p.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 

### OPTIONS
[![](https://i.imgur.com/pyaNUG3l.png)](https://i.imgur.com/pyaNUG3.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 

### AWARDED POINTS

[![](https://i.imgur.com/QBbikNgl.png)](https://i.imgur.com/QBbikNg.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 

### STYLE

[![](https://i.imgur.com/iSgPgJP.png)](https://i.imgur.com/iSgPgJP.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 


## OVERLAY UPDATER

> **NOTE:** You must launch from within Streamlabs Chatbot. 

The application will open, and if there is an update it will tell you. You click on the `Download & Update` button. 

> **NOTE:** Applying the update will close down Streamlabs Chatbot.

[![](https://i.imgur.com/YKIGYDul.png)](https://i.imgur.com/YKIGYDu.png)

## OVERLAY SETUP IN OBS / SLOBS 

- Add a new `Browser Source` in OBS / SLOBS  
[![](https://i.imgur.com/TAMQkeql.png)](https://i.imgur.com/TAMQkeq.png)
- **DO NOT** check `Local File`. To get the URL of the overlay, you can click on the `OPEN OVERLAY IN BROWSER` and copy the URL from your browser address bar.
- Set the `width` and `height` to the resolution of your `Base (Canvas) Resolution`. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  
[![](https://i.imgur.com/RRjVAFGl.png)](https://i.imgur.com/RRjVAFG.png)
