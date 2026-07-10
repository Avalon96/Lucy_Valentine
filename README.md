# Lucy Commands

## Interacting with Lucy
Possible interactions Lucy will respond to are:
* Reacting to her messages with LucyPat
* Sending LucyPat in a message
---

## Commands
### Use command
```<command_prefix><command_name>```
### Add Command
```<command_prefix>cmd <command_name> <response>```

### Add Multiple Commands
```
<command_prefix>batch
<command_name> <response>
<command_name2> <response2>
<command_name3> <response3> 
...
```

### Delete Command
```<command_prefix>del <command_name>```

### Delete Multiple Commands
```
<command_prefix>batchdel
<command_name>
<command_name2>
<command_name3> 
...
```

### Show All Commands
```<command_prefix>allcmd```

---
## JSON
### Export Commands JSON File
```<command_prefix>export```

Add --key flag to export only the command names, useful for !batchdel

```<command_prefix>export --key```

### Import Multiple Commands from a JSON File
```<command_prefix>import (attach JSON file)```

Add --overwrite flag to replace the custom_commands file

```<command_prefix>import --overwrite (attach JSON file)```

---
## Cringe Functionality
When a user is on the Cringe List, Lucy alters its response behavior toward them.

### Add to Cringe List
```<command_prefix>cringe <Display Name/Username/User ID>```

### Remove from Cringe List
```<command_prefix>uncringe <Display Name/Username/User ID>```

### Show Cringe List
```<command_prefix>allcringe```

---