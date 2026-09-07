```plantuml
title SIP-7701 Simple Transaction Flow

actor "User"
skinparam participantFontColor automatic
participant "Sila" #darkgreen
participant "AA_ENTRY_POINT" #darkgreen
participant "Sender Contract" #darkorchid
participant "Target Contract" #darkred

"User" -> "Sila": Submit AA transaction
note right of "Sila": execute\nAA transaction\nstate transition
"Sila" -> "AA_ENTRY_POINT":
|||
group Validation Phase
|||
"AA_ENTRY_POINT"->"Sender Contract": Validate AA Transaction\n""senderValidationData""
note over "Sender Contract": ""ACCEPTROLE 0xA1""
return valid: true
|||
end
|||
group Execution Phase
"AA_ENTRY_POINT"->"Sender Contract": Execute AA Transaction\n""senderExecutionData""
note over "Sender Contract": ""ACCEPTROLE 0xA3""
|||
"Sender Contract"->"Target Contract": AA Transaction\nExecution Body
|||
end
|||
```
