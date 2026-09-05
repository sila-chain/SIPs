This directory contains contract sources for SIP 3267 draft.

The audit of the contracts was paid for, now it is in progress.
(There are some FIXME/TODO comments for the auditors.)

The contracts are to be compiled with Solidity 0.7.6.

Dependencies (Node.js packages):

- @openzeppelin/contracts 3.3.0
- abdk-libraries-solidity 2.4.0

The contracts to be deployed are:
- SalaryWithDAO
- DefaultDAOInterface

The sources:
- [SRC1155/SRC1155.sol](./SRC1155/SRC1155.sol)
- [SRC1155/SRC1155TokenReceiver.sol](./SRC1155/SRC1155TokenReceiver.sol)
- [SRC1155/SRC1155WithTotals.sol](./SRC1155/SRC1155WithTotals.sol)
- [SRC1155/IERC1155.sol](./SRC1155/IERC1155.sol)
- [SRC1155/IERC1155TokenReceiver.sol](./SRC1155/IERC1155TokenReceiver.sol)
- [BaseBidOnAddresses.sol](./BaseBidOnAddresses.sol)
- [BaseLock.sol](./BaseLock.sol)
- [BaseRestorableSalary.sol](./BaseRestorableSalary.sol)
- [BaseSalary.sol](./BaseSalary.sol)
- [BidOnAddresses.sol](./BidOnAddresses.sol)
- [DAOInterface.sol](./DAOInterface.sol)
- [DefaultDAOInterface.sol](./DefaultDAOInterface.sol)
- [Salary.sol](./Salary.sol)
- [SalaryWithDAO.sol](./SalaryWithDAO.sol)