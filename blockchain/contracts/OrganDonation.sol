// SPDX-License-Identifier: MIT
pragma solidity >=0.8.19 <0.9.0;

/**
 * @title OrganDonation
 * @dev Stabilized Smart Contract for Organ Donation Tracking System.
 * Optimized for MCA Project Viva & Demo.
 */
contract OrganDonation {
    enum OrganStatus { Available, Matched, Transplanted }

    struct Donor {
        uint256 id;
        string name;
        string organType;
        string hospitalId;
        bool isApproved;
        uint256 timestamp;
        OrganStatus status;
    }

    uint256 public donorCount = 0;
    mapping(uint256 => Donor) public donors;

    event DonorRegistered(
        uint256 indexed id,
        string name,
        string organType,
        string hospitalId,
        uint256 timestamp
    );

    event OrganMatched(uint256 indexed id, string hospitalId, uint256 timestamp);

    /**
     * @dev Registers a new donor on the blockchain.
     */
    function registerDonor(
        string memory _name,
        string memory _organType,
        string memory _hospitalId
    ) public returns (uint256) {
        require(bytes(_name).length > 0, "Name is required");
        require(bytes(_organType).length > 0, "Organ type is required");
        
        donorCount++;
        donors[donorCount] = Donor({
            id: donorCount,
            name: _name,
            organType: _organType,
            hospitalId: _hospitalId,
            isApproved: true,
            timestamp: block.timestamp,
            status: OrganStatus.Available
        });

        emit DonorRegistered(donorCount, _name, _organType, _hospitalId, block.timestamp);
        return donorCount;
    }

    /**
     * @dev Retrieves donor details by ID.
     */
    function getDonor(uint256 _id) public view returns (
        uint256 id,
        string memory name,
        string memory organType,
        string memory hospitalId,
        bool isApproved,
        uint256 timestamp
    ) {
        require(_id > 0 && _id <= donorCount, "Invalid donor ID");
        Donor storage donor = donors[_id];
        return (
            donor.id,
            donor.name,
            donor.organType,
            donor.hospitalId,
            donor.isApproved,
            donor.timestamp
        );
    }

    /**
     * @dev Updates donor status to Matched.
     */
    function matchOrgan(uint256 _id, string memory _hospitalId) public {
        require(_id > 0 && _id <= donorCount, "Invalid donor ID");
        require(donors[_id].status == OrganStatus.Available, "Already matched or transplanted");
        
        donors[_id].status = OrganStatus.Matched;
        emit OrganMatched(_id, _hospitalId, block.timestamp);
    }
}
