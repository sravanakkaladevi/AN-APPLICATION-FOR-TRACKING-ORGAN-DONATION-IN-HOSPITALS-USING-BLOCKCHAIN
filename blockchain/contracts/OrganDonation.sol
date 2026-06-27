// SPDX-License-Identifier: MIT
pragma solidity >=0.8.19 <0.9.0;

/**
 * @title OrganDonation
 * @dev Smart Contract for Organ Donation Tracking System.
 * Records organ registration, matching, and transplant events on the blockchain
 * for an immutable audit trail.
 */
contract OrganDonation {
    enum OrganStatus { Available, Matched, Transplanted }
    enum RecipientStatus { Requested, OnBlockchain, Matched, Transplanted }

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

    struct RecipientRecord {
        uint256 id;
        string recipientId;
        string fullName;
        string bloodGroup;
        string organNeeded;
        string hospitalName;
        uint256 timestamp;
        RecipientStatus status;
        address recordedBy;
    }

    uint256 public organCount = 0;
    mapping(uint256 => Organ) public organs;

    uint256 public recipientCount = 0;
    mapping(uint256 => RecipientRecord) public recipients;

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

    event RecipientRegistered(
        uint256 indexed id,
        string recipientId,
        string fullName,
        string bloodGroup,
        string organNeeded,
        string hospitalName,
        uint256 timestamp,
        address indexed recordedBy
    );

    event RecipientStatusUpdated(uint256 indexed id, RecipientStatus status, uint256 timestamp);

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

    function registerRecipient(
        string memory _recipientId,
        string memory _fullName,
        string memory _bloodGroup,
        string memory _organNeeded,
        string memory _hospitalName
    ) public returns (uint256) {
        require(bytes(_recipientId).length > 0, "Recipient ID is required");
        require(bytes(_fullName).length > 0, "Full name is required");
        require(bytes(_bloodGroup).length > 0, "Blood group is required");
        require(bytes(_organNeeded).length > 0, "Organ needed is required");
        require(bytes(_hospitalName).length > 0, "Hospital name is required");

        recipientCount++;
        recipients[recipientCount] = RecipientRecord({
            id: recipientCount,
            recipientId: _recipientId,
            fullName: _fullName,
            bloodGroup: _bloodGroup,
            organNeeded: _organNeeded,
            hospitalName: _hospitalName,
            timestamp: block.timestamp,
            status: RecipientStatus.OnBlockchain,
            recordedBy: msg.sender
        });

        emit RecipientRegistered(
            recipientCount,
            _recipientId,
            _fullName,
            _bloodGroup,
            _organNeeded,
            _hospitalName,
            block.timestamp,
            msg.sender
        );

        return recipientCount;
    }

    function updateRecipientStatus(uint256 _id, RecipientStatus _status) public {
        require(_id > 0 && _id <= recipientCount, "Invalid recipient ID");
        recipients[_id].status = _status;
        emit RecipientStatusUpdated(_id, _status, block.timestamp);
    }

    function matchOrgan(uint256 _id, string memory _recipientHospitalName) public {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        require(organ.status == OrganStatus.Available, "Organ is not available");
        require(bytes(_recipientHospitalName).length > 0, "Recipient hospital is required");

        organ.status = OrganStatus.Matched;
        organ.recipientHospitalName = _recipientHospitalName;
        emit OrganMatched(_id, _recipientHospitalName, block.timestamp);
    }

    // Overloaded matchOrgan that also updates recipient status if mapped
    function matchOrganWithRecipient(uint256 _id, string memory _recipientHospitalName, uint256 _recipientBlockchainId) public {
        matchOrgan(_id, _recipientHospitalName);
        updateRecipientStatus(_recipientBlockchainId, RecipientStatus.Matched);
    }

    function completeTransplant(uint256 _id) public {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        require(organ.status == OrganStatus.Matched, "Organ is not matched yet");

        organ.status = OrganStatus.Transplanted;
        emit OrganTransplanted(_id, block.timestamp);
    }

    function completeTransplantWithRecipient(uint256 _id, uint256 _recipientBlockchainId) public {
        completeTransplant(_id);
        updateRecipientStatus(_recipientBlockchainId, RecipientStatus.Transplanted);
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
}
