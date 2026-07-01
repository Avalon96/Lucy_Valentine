# Lucy Commands

## Interacting with Lucy
Possible interactions Lucy will respond to are:
* Reacting to her messages with LucyPat
* Sending LucyPat in a message
---

## Commands
### Use command
```!<command_name>```
### Add Command
```!cmd !<command_name> <response>```

### Add Multiple Commands
```
!batch
!<command_name> <response>
!<command_name2> <response2>
!<command_name3> <response3>
...
```

### Delete Command
```!del !<command_name>```

### Show All Commands
```!allcmd```

---
## JSON
### Export Commands JSON File
```!export```

### Import Multiple Commands from a JSON File
```!json (attach JSON file)```

```!json (paste JSON format)```

---
## Cringe Functionality
When a user is on the Cringe List, the bot alters its response behavior toward them.

### Add to Cringe List
```!cringe <Display Name/Username/User ID>```

### Remove from Cringe List
```!uncringe <Display Name/Username/User ID>```

### Show Cringe List
```!allcringe```

---