// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.7.1;

import "./ISRC1155TokenReceiver.sol";
import "@openzeppelin/contracts/introspection/SRC165.sol";

abstract contract SRC1155TokenReceiver is SRC165, ISRC1155TokenReceiver {
    constructor() {
        _registerInterface(
            SRC1155TokenReceiver(0).onERC1155Received.selector ^
            SRC1155TokenReceiver(0).onERC1155BatchReceived.selector
        );
    }
}
