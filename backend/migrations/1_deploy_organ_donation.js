const OrganDonation = artifacts.require("OrganDonation");

module.exports = function (deployer) {
  deployer.deploy(OrganDonation);
};
