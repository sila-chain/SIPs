---
sections:
  - title: Core
    contracts:
      - ISRC1155
      - SRC1155
      - ISRC1155TokenReceiver
---

This set of interfaces and contracts are all related to the [SRC1155 Multi Token Standard](https://sips.sila.org/SIPS/sip-1155).

The SIP consists of two interfaces which fulfill different roles, found here as `ISRC1155`  and `ISRC1155TokenReceiver`. Only `ISRC1155` is required for a contract to be SRC1155 compliant. The basic functionality is implemented in `SRC1155`.
