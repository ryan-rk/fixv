# FIXV (Fix Message Viewer)

An application for decoding and previewing FIX message in tree-like structure. It will shows the tag number, tag name as well as the corresponding values (including expansion on enums type) for each field presents in the message. A lot of user friendly features are also included for fast and smooth user experience.
<br>
<br>
<br>
## Installations
Download the prebuilt binaries from the release section for corresponding platform (Windows and MacOS) and extract it to start using it.
For Windows, double clicking the FIXV.exe should launch the application.
For MacOS, aside from the .app file there will also be a directory "FIXV". Double clicking on the FIXV.app should launch the application.
<br>
<br>
The prebuilt binaries are built and tested on: Windows 10 and MacOS 13.2. If the user prefers to build the application from source, or run the python code directly, the required python modules are:
<br>
1. PyQt6
2. Modified version of Quickfix library which can be found at my github: [https://github.com/ryan-rk/quickfix](https://github.com/ryan-rk/quickfix).
3. Pyinstaller (for building into an executable)
<br>
<br>
<br>
## Configs
At the moment, a config file named "app_config.ini" is required in order for the application to work properly. The config file can be found in the same directory as the executable for Windows users, and inside the directory FIXV for MacOS users. Since the application is built on top of the quickfix python module, <b>Fix data dictionaries in quickfix .xml format</b> are also required. The paths to the data dictionaries can be provided in the config file. If custom dictionaries are not provided, the application will use the default dictionaries provided by quickfix library.
<br>
<br>
The config file also provides some options to set the default behavior of the application features. This will be further expanded in future to provide more customizing options.
<br>
<br>
<br>
## Usage
To decode and view FIX message with this application, copy any FIX message and click the <b>[Paste]</b> (Shortcut: ctrl+p / cmd+p) button. The message in the clipboard will be pasted onto the message label and directly decoded below it. To re-generate the message, click on <b>[Re-Parse]</b> (Shortcut: ctrl+r / cmd+r) button. Clicking on the message label will open up the message editor, for modifying the message string. The FIX message can be separated by any viable delimiter, however the <b>[Delimiter]</b> field should be updated to reflect that. In the case where the copied message is being separated by SOH character, the delimiter can be left at the default pipe symbol: " | ". The message tree will be expanded automatically after parsing, if this is not the desired behavior, the user can change the "ExpandOnLaunch" option in the config file.
<br>
<br>
<br>
## Features
1. <b>Always On Top</b>
<br>
This is the default behavior of the application, by staying as the top-most window at all time (even when it is not the currently focussed window), it will be much more convenient for the user to view the message structure at any moment. This feature can be disabled from the config file or from the <b>[View]</b> menu bar item. This feature also complements perfectly with the following Auto-Paste feature.
<br>
<br>
2. <b>Auto-Paste</b>
<br>
By turning this feature on, any messages that are copied to the clipboard at any time will be directly pasted and decoded in the application. This allows for a quicker message viewing experience as the user does not need to switch back to the application to paste the message. This is especially useful to view messages in application such as Windows Terminal, in which any selected text is directly copied to the clipboard. However due to the way MacOS works, this feature does not work perfectly on the system as the user is required to switch back to the FIXV application after copying the message.
<br>
<br>
3. <b>Compact Form</b>
<br>
The application can be switched to a more compact form by clicking on the <b>[Compact]</b> button (Shortcut: ctrl+m / cmd+m). There is also an option to enable the application to auto switch to compact mode when it is not in focus, and switch back when it is in focus. This option can be accessed from the <b>[View]</b> menu bar.
<br>
<br>
4. <b>Error Message</b>
<br>
There will be error messages showing up when there is something wrong such as parsing message. These error messages can be in the way when using the Auto-Paste feature, therefore an option is also added to only show the error in status bar (bottom of the application window). This option can be accessed from the <b>[View]</b> menu bar or set up in the config file.