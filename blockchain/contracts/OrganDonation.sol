// SPDX-License-Identifier: MIT
pragma solidity >=0.8.19 <0.9.0;

/**
 * @title OrganDonation
 * @dev Unified Smart Contract for Organ Donation Tracking System.
 * Supports both legacy/REST API methods (Donor mapping) and Django Core methods (Organ mapping).
 */
contract OrganDonation {
    enum OrganStatus { Available, Matched, Transplanted }

    // --- VERSION A (Legacy API / Tests compatibility) ---
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

    // --- VERSION B (Django Core application integration) ---
    struct Organ {
        uint256 id;
        string donorId;
        string donorName;
        string organType;
        string hospitalName;
        string doctorName;
        uint256 timestamp;
        OrganStatus status;
        address recordedBy;
        string recipientHospitalName;
    }

    uint256 public organCount = 0;
    mapping(uint256 => Organ) public organs;

    event DonationRegistered(
        uint256 indexed id,
        string donorId,
        string donorName,
        string organType,
        string hospitalName,
        string doctorName,
        uint256 timestamp,
        address indexed recordedBy
    );

    event OrganMatched(uint256 indexed id, string recipientHospitalName, uint256 timestamp);
    event OrganTransplanted(uint256 indexed id, uint256 timestamp);

    // --- VERSION A FUNCTIONS ---
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

    // --- VERSION B FUNCTIONS ---
    function registerDonation(
        string memory _donorId,
        string memory _donorName,
        string memory _organType,
        string memory _hospitalName,
        string memory _doctorName
    ) public returns (uint256) {
        require(bytes(_donorId).length > 0, "Donor ID is required");
        require(bytes(_donorName).length > 0, "Donor name is required");
        require(bytes(_organType).length > 0, "Organ type is required");
        require(bytes(_hospitalName).length > 0, "Hospital name is required");

        organCount++;
        organs[organCount] = Organ({
            id: organCount,
            donorId: _donorId,
            donorName: _donorName,
            organType: _organType,
            hospitalName: _hospitalName,
            doctorName: _doctorName,
            timestamp: block.timestamp,
            status: OrganStatus.Available,
            recordedBy: msg.sender,
            recipientHospitalName: ""
        });

        emit DonationRegistered(
            organCount,
            _donorId,
            _donorName,
            _organType,
            _hospitalName,
            _doctorName,
            block.timestamp,
            msg.sender
        );

        return organCount;
    }

    function completeTransplant(uint256 _id) public {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        require(organ.status == OrganStatus.Matched, "Organ is not matched yet");
        
        organ.status = OrganStatus.Transplanted;
        emit OrganTransplanted(_id, block.timestamp);
    }

    function getOrgan(uint256 _id) public view returns (
        uint256 id,
        string memory donorId,
        string memory donorName,
        string memory organType,
        string memory hospitalName,
        string memory doctorName,
        uint256 timestamp,
        OrganStatus status,
        address recordedBy,
        string memory recipientHospitalName
    ) {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        return (
            organ.id,
            organ.donorId,
            organ.donorName,
            organ.organType,
            organ.hospitalName,
            organ.doctorName,
            organ.timestamp,
            organ.status,
            organ.recordedBy,
            organ.recipientHospitalName
        );
    }

    // --- SHARED / UNIFIED FUNCTIONS ---
    function matchOrgan(uint256 _id, string memory _recipientHospitalName) public {
        bool matchedAny = false;

        if (_id > 0 && _id <= organCount) {
            Organ storage organ = organs[_id];
            require(organ.status == OrganStatus.Available, "Organ is not available");
            require(bytes(_recipientHospitalName).length > 0, "Recipient hospital is required");
            
            organ.status = OrganStatus.Matched;
            organ.recipientHospitalName = _recipientHospitalName;
            emit OrganMatched(_id, _recipientHospitalName, block.timestamp);
            matchedAny = true;
        }

        if (_id > 0 && _id <= donorCount) {
            require(donors[_id].status == OrganStatus.Available, "Already matched or transplanted");
            donors[_id].status = OrganStatus.Matched;
            emit OrganMatched(_id, _recipientHospitalName, block.timestamp);
            matchedAny = true;
        }

        require(matchedAny, "Invalid ID");
    }
}
