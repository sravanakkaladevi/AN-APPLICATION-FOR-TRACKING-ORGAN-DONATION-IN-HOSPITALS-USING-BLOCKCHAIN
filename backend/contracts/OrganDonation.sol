// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

contract OrganDonation {
    enum OrganStatus { Available, Matched, Transplanted }

    struct Organ {
        uint256 id;
        string donorHash;
        string organType;
        string bloodGroup;
        OrganStatus status;
        address hospital;
        address recipientHospital;
    }

    uint256 public organCount = 0;
    mapping(uint256 => Organ) public organs;

    event OrganAdded(uint256 id, string donorHash, string organType, string bloodGroup, address hospital);
    event OrganMatched(uint256 id, address recipientHospital);
    event OrganTransplanted(uint256 id);

    function addOrgan(string memory _donorHash, string memory _organType, string memory _bloodGroup) public {
        organCount++;
        organs[organCount] = Organ({
            id: organCount,
            donorHash: _donorHash,
            organType: _organType,
            bloodGroup: _bloodGroup,
            status: OrganStatus.Available,
            hospital: msg.sender,
            recipientHospital: address(0)
        });
        emit OrganAdded(organCount, _donorHash, _organType, _bloodGroup, msg.sender);
    }

    function matchOrgan(uint256 _id, address _recipientHospital) public {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        require(organ.status == OrganStatus.Available, "Organ is not available");
        
        organ.status = OrganStatus.Matched;
        organ.recipientHospital = _recipientHospital;
        emit OrganMatched(_id, _recipientHospital);
    }

    function completeTransplant(uint256 _id) public {
        require(_id > 0 && _id <= organCount, "Invalid organ ID");
        Organ storage organ = organs[_id];
        require(organ.status == OrganStatus.Matched, "Organ is not matched yet");
        
        organ.status = OrganStatus.Transplanted;
        emit OrganTransplanted(_id);
    }
}
