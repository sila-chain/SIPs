// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.7.1;

import "@openzeppelin/contracts/introspection/ISRC165.sol";

/**
    @title SRC-1155 Multi Token Standard basic interface
    @dev See https://sips.sila.org/SIPS/sip-1155
 */
abstract contract ISRC1155 is ISRC165 {
    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);

    event TransferBatch(address indexed operator, address indexed from, address indexed to, uint256[] ids, uint256[] values);

    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    event URI(string value, uint256 indexed id);

    function balanceOf(address owner, uint256 id) public view virtual returns (uint256);

    function balanceOfBatch(address[] memory owners, uint256[] memory ids) public view virtual returns (uint256[] memory);

    function setApprovalForAll(address operator, bool approved) external virtual;

    function isApprovedForAll(address owner, address operator) external view virtual returns (bool);

    function safeTransferFrom(address from, address to, uint256 id, uint256 value, bytes calldata data) external virtual;

    function safeBatchTransferFrom(address from, address to, uint256[] calldata ids, uint256[] calldata values, bytes calldata data) external virtual;
}
